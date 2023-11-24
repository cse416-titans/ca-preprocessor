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

# load in the vtd and district shapefiles
units = gpd.read_file("azjson.json").to_crs(32030)

print(list(units.columns))

# configure updaters for the recom chain
elections = [Election("PRED20", {"Dem": "G20PREDBID", "Rep": "G20PRERTRU"})]
my_updaters = {"population": updaters.Tally("Total_Population", alias="population")}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

# print(units)
# print(districts)

# assign districts to vtds
# assignment = maup.assign(units, districts)


# print(assignment.isna().sum())

# units["SLDL_DIST"] = assignment

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
    total_steps=1000,
)

i = 0
for partition in chain:
    if i > 100:
        break

    i += 1

    if i % 10 == 0:
        print(i)
        # update unit's assignment
        units["SLDL_DIST"] = partition.assignment

        # save new units into json
        units.to_file("./units/az_pl2020_vtd_" + str(i) + ".json", driver="GeoJSON")

        partition.plot(units, cmap="tab20")
        plt.axis("off")
        plt.savefig("./plots/az_pl2020_vtd_" + str(i) + ".png")

        # To see the plot, uncomment the following lines
        # plt.axis("off")
        # plt.show()

"""
real_life_plan = Partition(graph, "SLDIST", {"population": "TOTPOP"})
real_life_plan.plot(units, cmap="tab20")
plt.axis("off")
plt.show()
"""