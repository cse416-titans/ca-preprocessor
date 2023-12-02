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
import multiprocessing as mp
from multiprocessing import Pool, Manager
import math
import maup

"""
REQUIRED FILES:
1. azjson.json (aggregated precinct level census + election + district_plan shapefile)
"""

# default values
NUM_CORES = 0
NUM_PROJECTED_PLANS = 0


def initWorker(state, num_cores, num_plans, ensembleId):
    global NUM_PROJECTED_PLANS_PER_CORE
    global NUM_PROJECTED_PLANS
    global NUM_CORES
    global arr  # array of initial partitions per core
    global units
    global ensemble_id
    ensemble_id = ensembleId
    global stateAbbr
    stateAbbr = state

    NUM_CORES = num_cores
    NUM_PROJECTED_PLANS = num_plans
    NUM_PROJECTED_PLANS_PER_CORE = math.ceil(NUM_PROJECTED_PLANS / NUM_CORES)

    global STEP

    STEP = 1000

    n = NUM_PROJECTED_PLANS_PER_CORE

    # load in the json
    units = gpd.read_file("azjson.json").to_crs(32030)

    # configure updaters for the recom chain
    elections = [Election("PRED20", {"Dem": "Democratic", "Rep": "Republic"})]
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

    pop_constraint = constraints.within_percent_of_ideal_population(
        initial_partition, 0.10
    )

    chain = MarkovChain(
        proposal=proposal,
        constraints=[pop_constraint, compactness_bound],
        accept=accept.always_accept,
        initial_state=initial_partition,
        total_steps=STEP * NUM_CORES,
    )

    # save only every 1000th partition in the chain into an array
    arr = []
    i = 0
    for partition in chain.with_progress_bar():
        # print("Creating initial partitions: ", i)
        # pick only the last plan
        i += 1
        if i % STEP != 0:
            continue
        arr.append(partition)

    print("Done creating initial partitions.")
    print("Length of arr: ", len(arr))


def makeRandomPlansNoMaup(id):
    initial_partition = arr[id]

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
        total_steps=NUM_PROJECTED_PLANS_PER_CORE * STEP,
    )

    i = 0
    for partition in chain.with_progress_bar():
        i += 1
        if i % STEP != 0:
            continue
        fileId = i // STEP + (id) * NUM_PROJECTED_PLANS_PER_CORE
        units["SLDL_DIST"] = partition.assignment
        units["geometry"] = units["geometry"].to_crs(4326)
        units.to_file(
            f"./{stateAbbr}/ensemble-{ensemble_id}/units/plan-{fileId}.json",
            driver="GeoJSON",
        )

        partition.plot(units, cmap="tab20")
        plt.axis("off")
        plt.savefig(f"./{stateAbbr}/ensemble-{ensemble_id}/plots/plan-{fileId}.png")
        plt.close()

        units_copy = units.copy()
        districts = units_copy.dissolve(by="SLDL_DIST", aggfunc="sum")
        districts = districts.drop(columns=["PCTNUM", "NAME"])
        districts["geometry"] = districts["geometry"].buffer(0)
        districts["geometry"] = districts["geometry"].simplify(
            0.0001, preserve_topology=True
        )
        districts["geometry"] = districts["geometry"].apply(lambda p: close_holes(p))
        districts["geometry"] = districts["geometry"].to_crs(4326)

        print("Saving plan: ", fileId)
        districts.to_file(
            f"./{stateAbbr}/ensemble-{ensemble_id}/districts/plan-{fileId}.json",
            driver="GeoJSON",
        )

        # To see the plot, uncomment the following lines
        # plt.axis("off")
        # plt.show()


def start(state, num_cores, num_plans, ensembleId):
    """
    [1...NUM_CORES] folders be made in the units, plots, districts, districts_reassigned, plots_reassigned folders.
    Each folder will have NUM_PLANS_PER_CORE plans inside it.
    """

    start_time = datetime.now()

    func = partial(makeRandomPlansNoMaup)

    with Pool(
        initializer=initWorker,
        initargs=(state, num_cores, num_plans, ensembleId),
        processes=num_cores,
    ) as pool:
        result = pool.map(func, range(num_cores))
        pool.close()
        pool.join()

    end_time = datetime.now()

    print("Duration: ", end_time - start_time)


if __name__ == "__main__":
    pass
