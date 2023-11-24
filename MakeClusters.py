from OptimalTransport import Pair
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
    graph,
)
from gerrychain.proposals import recom
from functools import partial
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
import numpy as np
from sklearn.manifold import MDS
from datetime import datetime
from os import makedirs

import multiprocessing as mp
from multiprocessing import Pool, Manager, current_process

import math
from random import random


MAX_NUM_PLANS = 1000
MAX_NUM_COMPARISON = MAX_NUM_PLANS * MAX_NUM_PLANS / 2
NUM_PLANS = 5
NUM_COMPARISON = NUM_PLANS * NUM_PLANS / 2
NUM_CORES = 4  # 16
NUM_COMPARISON_PER_CORE = math.ceil(NUM_COMPARISON / NUM_CORES)


# initialize worker processes
def initWorker():
    global queue_core
    global distance_matrix

    distance_matrix = np.zeros((NUM_PLANS, NUM_PLANS))

    # make a list of (i,j) tuples where i <=j and i,j are in [0, NUM_PLANS)
    comparisons_total = []
    for i in range(NUM_PLANS):
        for j in range(i, NUM_PLANS):
            comparisons_total.append((i, j))

    queue_core = [[] for _ in range(NUM_CORES)]

    for i, comparison in enumerate(comparisons_total):
        queue_core[i % NUM_CORES].append(comparison)

    # print("queue_core:", queue_core[0])
    # print("len(queue_core):", len(queue_core))
    # print("len(queue_core[0]):", len(queue_core[0]))


def makeCluster(arg):
    start_time = datetime.now()

    queue = queue_core[arg]

    for i in range(len(queue)):
        print("i: ", i, ", queue[i]: ", queue[i])
        if queue[i][0] != queue[i][1]:
            distance_matrix[queue[i][0], queue[i][1]] = 1 + random() * 2

        """
        districtsA = gpd.read_file(f"./units/az_pl2020_vtd_{queue[i][0]}.json")
        graphA = Graph.from_geodataframe(districtsA)

        districtsB = gpd.read_file(f"./units/az_pl2020_vtd_{queue[i][1]}.json")
        graphB = Graph.from_geodataframe(districtsB)

        # calculate distance
        distance_matrix[queue[i][0], queue[i][1]] = Pair(
            GeographicPartition(graphA, assignment="SLDL_DIST"),
            GeographicPartition(graphB, assignment="SLDL_DIST"),
        ).distance
        """

    return distance_matrix

    """
    n = 9  # number of plans

    distances = np.zeros((n, n))

    # configure plans
    plans = []
    for i in range(2000, 11000, 1000):
        districts = gpd.read_file(f"./units/az_pl2020_vtd_{i}.json")
        graph = Graph.from_geodataframe(districts, ignore_errors=True)
        plans.append(GeographicPartition(graph, assignment="SLDL_DIST"))

    for outer_idx, outer_plan in tqdm(enumerate(plans)):
        for inner_idx in range(outer_idx + 1, n):
            print("inner_idx: ", inner_idx)
            inner_plan = plans[inner_idx]
            distances[outer_idx, inner_idx] = Pair(outer_plan, inner_plan).distance

    print(distances)

    mds = MDS(n_components=2, random_state=0, dissimilarity="precomputed")
    pos = mds.fit(distances).embedding_

    # save image
    plt.scatter(pos[:, 0], pos[:, 1])
    plt.savefig("./clusters/mds.png")

    end_time = datetime.now()

    print("Duration: ", end_time - start_time)
    """


if __name__ == "__main__":
    makedirs("clusters", exist_ok=True)

    with Pool(initializer=initWorker, processes=NUM_CORES) as pool:
        res = pool.map(makeCluster, range(NUM_CORES))
        pool.close()
        pool.join()

    print(current_process().name)

    # aggregate all arrays in res into one
    agg = np.zeros((NUM_PLANS, NUM_PLANS))

    for i in range(len(res)):
        mask = agg == 0
        agg[mask] = res[i][mask]

    # get last updated distance matrix
    # print("agg:", agg)

    # print("distances:", distances)

    # get symmetrized distance matrix
    distances = np.maximum(agg, agg.transpose())

    print(distances)

    mds = MDS(n_components=2, random_state=0, dissimilarity="precomputed")
    pos = mds.fit(distances).embedding_

    print(pos)
