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
import multiprocessing as mp
from multiprocessing import Pool, Manager
import math

import maup

"""
Use this script when you want to run ReCom with disagggregated precinct level data.
"""

"""
REQUIRED FILES:
1. azjson.json (aggregated precinct level census + election + district_plan shapefile)
"""

# create directory named units, plots, districts, districts_reassigned, plots_reassigned if they don't exist
makedirs("units", exist_ok=True)
makedirs("plots", exist_ok=True)
makedirs("districts", exist_ok=True)
makedirs("districts_reassigned", exist_ok=True)
makedirs("plots_reassigned", exist_ok=True)

NUM_CORES = 10


def initWorker():
    global NUM_PROJECTED_PLANS_PER_CORE
    global NUM_CORES
    global arr
    global units

    NUM_PROJECTED_PLANS = 20
    NUM_PROJECTED_PLANS_PER_CORE = math.ceil(NUM_PROJECTED_PLANS / NUM_CORES)

    STEP = 1000

    # load in the vtd and district shapefiles
    units = gpd.read_file("az_pl2020_vtd.zip").to_crs(32030)
    districts = gpd.read_file("az_sl_adopted_2022.zip").to_crs(32030)

    """
    TODO: Implement the unimplemented followings:
    1. Import the precinct level election shapefile (precinct level presidential election results)
    2. Convert the precinct level election shapefile into a dataframe (Call it "elections")
    3. Merge elections into units
    """

    """
    TODO: Implement the half-implemented followings:
    1. Rename/drop column in units & districts dataframe before assigning districts to units using maup.assign(units, districts)
        1) Make Total_Population column in units dataframe.
        2) 
    1. Fully configure updaters for the recom chain
        1) Add the election_updaters to my_updaters (uncomment related code: line 78-80)
    """

    # configure updaters for the recom chain

    my_updaters = {"population": updaters.Tally("POP100", alias="population")}
    # elections = [Election("PRED20", {"Dem": "G20PREDBID", "Rep": "G20PRERTRU"})]
    # election_updaters = {election.name: election for election in elections}
    # my_updaters.update(election_updaters)

    # assign districts to vtds
    assignment = maup.assign(units, districts)

    # check if there is any null value in the assignment
    print(assignment.isna().sum())

    # add the assignment to the units dataframe
    units["SLDIST"] = assignment

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

    pop_constraint = constraints.within_percent_of_ideal_population(
        initial_partition, 0.10
    )

    chain = MarkovChain(
        proposal=proposal,
        constraints=[pop_constraint, compactness_bound],
        accept=accept.always_accept,
        initial_state=initial_partition,
        total_steps=STEP * NUM_CORES * NUM_PROJECTED_PLANS_PER_CORE,
    )

    # save only every 1000th partition in the chain into an array
    arr = []
    i = 0
    for partition in chain.with_progress_bar():
        i += 1
        # pick only the last plan
        if i % STEP != 0:
            continue
        arr.append(partition)


def makeRandomPlansNoMaup(id, lock):
    start_time = datetime.now()

    for x in range(NUM_PROJECTED_PLANS_PER_CORE):
        procId = id + 1

        lock.acquire()

        print(
            "\nprocId: ", procId, ", progress: ", x, "/", NUM_PROJECTED_PLANS_PER_CORE
        )

        partition = arr[x + (procId - 1) * NUM_PROJECTED_PLANS_PER_CORE]

        # update unit's assignment
        units["SLDL_DIST"] = partition.assignment

        # convert unit's coordinates to lat/lon
        units["geometry"] = units["geometry"].to_crs(4326)

        # save new units into json
        units.to_file(
            f"./units/az_pl2020_vtd_{procId + x + procId-1}.json",
            driver="GeoJSON",
        )

        partition.plot(units, cmap="tab20")
        plt.axis("off")
        plt.savefig(f"./plots/az_pl2020_vtd_{procId + x + procId-1}.png")
        plt.close()

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
            f"./districts/az_pl2020_sldl_{procId + x + procId-1}.json",
            driver="GeoJSON",
        )

        # To see the plot, uncomment the following lines
        # plt.axis("off")
        # plt.show()

        lock.release()

    end_time = datetime.now()

    print("Duration: ", end_time - start_time)


def start():
    """
    [1...NUM_CORES] folders be made in the units, plots, districts, districts_reassigned, plots_reassigned folders.
    Each folder will have NUM_PLANS_PER_CORE plans inside it.
    """

    m = Manager()
    l = m.Lock()

    func = partial(makeRandomPlansNoMaup, lock=l)

    with Pool(initializer=initWorker, processes=NUM_CORES) as pool:
        result = pool.map(func, range(NUM_CORES))

    pool.close()
    pool.join()


if __name__ == "__main__":
    start()
