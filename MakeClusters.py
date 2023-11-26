from OptimalTransport import Pair
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import numpy as np

from sklearn.manifold import MDS
from sklearn.cluster import KMeans

from datetime import datetime
from os import makedirs

import multiprocessing as mp
from multiprocessing import Pool, Manager, current_process

import math
from random import random


MAX_NUM_PLANS = 1000
MAX_NUM_COMPARISON = MAX_NUM_PLANS * MAX_NUM_PLANS / 2
NUM_PLANS = 100
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

    # use this for k-means clustering
    print(pos)

    # using pos, run k-means clustering with elbow method to find optimal number of clusters
    distortions = []
    K = range(1, NUM_PLANS)

    for k in K:
        kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit(pos)
        distortions.append(kmeanModel.inertia_)

    plt.figure(figsize=(16, 8))
    plt.plot(K, distortions, "bx-")
    plt.xlabel("k")
    plt.ylabel("Distortion")
    plt.title("The Elbow Method showing the optimal k")
    plt.savefig("./clusters/elbow.png")
    plt.close()

    print("distortions:", distortions)

    # calculate elbow point
    elbow = 0
    for i in range(len(distortions) - 1):
        print("i:", i)
        print(abs(distortions[i + 1] - distortions[i]))
        if abs(distortions[i + 1] - distortions[i]) < 1:
            elbow = i + 1
            break

    print("elbow:", elbow)

    # perform k-means clustering with elbow point based on pos
    kmeans = KMeans(n_clusters=elbow)
    kmeans.fit(pos)
    y_kmeans = kmeans.predict(pos)

    print("y_kmeans:", y_kmeans)
    print("kmeans.cluster_centers_:", kmeans.cluster_centers_)

    # plot clusters
    plt.scatter(pos[:, 0], pos[:, 1], c=y_kmeans, s=50, cmap="viridis")
    centers = kmeans.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1], c="black", s=200, alpha=0.5)
    plt.savefig("./clusters/clusters.png")
    plt.close()
