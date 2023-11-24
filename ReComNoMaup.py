import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from gerrychain import (
    GeographicPartition,
    Partition,
    Graph,
    MarkovChain,
    proposals,
    updaters,
    constraints,
    accept,
    Election,
)

from gerrychain.proposals import recom
from functools import partial
from polygonUtil import close_holes

from datetime import datetime
from os import makedirs

"""
REQUIRED FILES:
1. azjson.json (aggregated precinct level census + election + district_plan shapefile)
"""

start_time = datetime.now()

# create directory named units, plots, districts, districts_reassigned, plots_reassigned if they don't exist
makedirs("units", exist_ok=True)
makedirs("plots", exist_ok=True)
makedirs("districts", exist_ok=True)
makedirs("districts_reassigned", exist_ok=True)
makedirs("plots_reassigned", exist_ok=True)

# load in the json
units = gpd.read_file("azjson.json").to_crs(32030)

# configure updaters for the recom chain
elections = [Election("PRED20", {"Dem": "G20PREDBID", "Rep": "G20PRERTRU"})]
my_updaters = {"population": updaters.Tally("Total_Population", alias="population")}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

graph = Graph.from_geodataframe(units)

initial_partition = GeographicPartition(
    graph, assignment="SLDL_DIST", updaters=my_updaters
)

ideal_population = sum(initial_partition["population"].values()) / len(
    initial_partition
)

proposal = partial(
    recom,
    pop_col="Total_Population",
    pop_target=ideal_population,
    epsilon=0.1,
    node_repeats=2,
)

compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]), 2 * len(initial_partition["cut_edges"])
)

pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.10)

chain = MarkovChain(
    proposal=proposal,
    constraints=[pop_constraint, compactness_bound],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=10000,
)

i = 0
for partition in chain:
    if i > 10000:
        break

    i += 1

    if i % 1000 == 0:
        print(i)
        # update unit's assignment
        units["SLDL_DIST"] = partition.assignment

        # convert unit's coordinates to lat/lon
        units["geometry"] = units["geometry"].to_crs(4326)

        # save new units into json
        units.to_file("./units/az_pl2020_vtd_" + str(i) + ".json", driver="GeoJSON")

        partition.plot(units, cmap="tab20")
        plt.axis("off")
        plt.savefig("./plots/az_pl2020_vtd_" + str(i) + ".png")

        units_copy = units.copy()

        # create a new dataframe which aggregates the units to the district level and for its geometry, takes the union of the unit geometries
        districts = units_copy.dissolve(by="SLDL_DIST", aggfunc="sum")

        # drop PCTNUM and PRECINCTNA column
        districts = districts.drop(columns=["PCTNUM", "PRECINCTNA"])

        # avoid self-intersection
        districts["geometry"] = districts["geometry"].buffer(0)

        # make geometry smooth
        districts["geometry"] = districts["geometry"].simplify(
            0.0001, preserve_topology=True
        )

        # fill in any holes in the geometry
        districts["geometry"] = districts["geometry"].apply(lambda p: close_holes(p))

        # print if the polygon is valid
        # print(districts["geometry"].is_valid)

        # save the districts into a json
        districts.to_file(
            "./districts/az_pl2020_sldl_" + str(i) + ".json", driver="GeoJSON"
        )

        # To see the plot, uncomment the following lines
        # plt.axis("off")
        # plt.show()

end_time = datetime.now()

print("Duration: ", end_time - start_time)