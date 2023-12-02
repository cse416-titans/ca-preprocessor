from OptimalTransport import Pair
from HammingDistance import hammingdistance

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

from gerrychain import GeographicPartition, Graph


MAX_NUM_PLANS = 1000
MAX_NUM_COMPARISON = MAX_NUM_PLANS * MAX_NUM_PLANS / 2

NUM_PLANS = 0
NUM_COMPARISON = 0
NUM_CORES = 0
NUM_COMPARISON_PER_CORE = 0

DISTANCEMEASURE_ID = 0


# initialize worker processes
def initWorker(state, num_cores, num_plans, id, ensembleId):
    global NUM_CORES
    global NUM_PLANS
    global NUM_COMPARISON
    global NUM_COMPARISON_PER_CORE

    global queue_core
    global distance_matrix
    global distancemeasure_id
    global ensemble_id
    global stateAbbr

    stateAbbr = state
    distancemeasure_id = id
    ensemble_id = ensembleId

    NUM_CORES = num_cores
    NUM_PLANS = num_plans
    NUM_COMPARISON = NUM_PLANS * NUM_PLANS / 2
    NUM_COMPARISON_PER_CORE = math.ceil(NUM_COMPARISON / NUM_CORES)

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

        districtsA = gpd.read_file(
            f"./{stateAbbr}/ensemble-{ensemble_id}/units/plan-{queue[i][0]+1}.json"
        )
        graphA = Graph.from_geodataframe(districtsA)

        districtsB = gpd.read_file(
            f"./{stateAbbr}/ensemble-{ensemble_id}/units/plan-{queue[i][1]+1}.json"
        )
        graphB = Graph.from_geodataframe(districtsB)

        # calculate distance
        if distancemeasure_id == 0:  # optimal transport
            """
            distance_matrix[queue[i][0], queue[i][1]] = Pair(
                GeographicPartition(graphA, assignment="SLDL_DIST"),
                GeographicPartition(graphB, assignment="SLDL_DIST"),
            ).distance
            """
            if queue[i][0] != queue[i][1]:
                distance_matrix[queue[i][0], queue[i][1]] = 1 + random() * 2
        elif distancemeasure_id == 1:  # Hamming distance
            """
            distance_matrix[queue[i][0], queue[i][1]] = hammingdistance(
                queue[i][0], queue[i][1]
            )
            """
            if queue[i][0] != queue[i][1]:
                distance_matrix[queue[i][0], queue[i][1]] = 1 + random() * 2
        elif distancemeasure_id == 2:  # Entropy distance
            if queue[i][0] != queue[i][1]:
                distance_matrix[queue[i][0], queue[i][1]] = 1 + random() * 2
        else:
            print("Invalid distance measure id.")
            exit()

    return distance_matrix


def start(state, id, num_cores, num_plans, ensembleId):
    makedirs(f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}", exist_ok=True)

    with Pool(
        initializer=initWorker,
        initargs=(state, num_cores, num_plans, id, ensembleId),
        processes=num_cores,
    ) as pool:
        res = pool.map(makeCluster, range(num_cores))
        pool.close()
        pool.join()

    print(current_process().name)

    # aggregate all arrays in res into one
    agg = np.zeros((num_plans, num_plans))
    for i in range(len(res)):
        mask = agg == 0
        agg[mask] = res[i][mask]

    # get symmetrized distance matrix
    distances = np.maximum(agg, agg.transpose())
    mds = MDS(n_components=2, random_state=0, dissimilarity="precomputed")
    pos = mds.fit(distances).embedding_

    # save distance matrix into a csv
    df = pd.DataFrame(distances)
    df.to_csv(
        f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}/distance-matrix-summary.csv"
    )

    # save pos into a csv
    df = pd.DataFrame(pos)
    df.to_csv(
        f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}/plan-mds-coordinates-summary.csv"
    )

    # using pos, run k-means clustering with elbow method to find optimal number of clusters
    distortions = []
    K = range(1, num_plans + 1)

    for k in K:
        kmeanModel = KMeans(n_clusters=k)
        kmeanModel.fit(pos)
        distortions.append(kmeanModel.inertia_)

    plt.figure(figsize=(16, 8))
    plt.plot(K, distortions, "bx-")
    plt.xlabel("k")
    plt.ylabel("Distortion")
    plt.title("The Elbow Method showing the optimal k")
    plt.savefig(f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}/elbowPlot.png")
    plt.close()

    # print("distortions:", distortions)

    # calculate elbow point
    elbow = 0
    for i in range(len(distortions) - 1):
        print("i:", i)
        print(abs(distortions[i + 1] - distortions[i]))
        if abs(distortions[i + 1] - distortions[i]) < 1:
            elbow = i + 1
            break

    # print("elbow:", elbow)

    if elbow == 0:
        elbow = num_plans

    # perform k-means clustering with elbow point based on pos
    kmeans = KMeans(n_clusters=elbow)
    kmeans.fit(pos)
    y_kmeans = kmeans.predict(pos)

    print("y_kmeans:", y_kmeans)
    print("kmeans.cluster_centers_:", kmeans.cluster_centers_)

    centers = kmeans.cluster_centers_

    # save cluster centers into a csv
    df = pd.DataFrame(centers)
    df.to_csv(
        f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}/cluster-centers-summary.csv"
    )

    # plot clusters
    plt.scatter(pos[:, 0], pos[:, 1], c=y_kmeans, s=50, cmap="viridis")
    plt.scatter(centers[:, 0], centers[:, 1], c="black", s=200, alpha=0.5)
    plt.savefig(f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}/clusterPlot.png")
    plt.close()

    # for all plans in district_reassigned folder, move them into their respective cluster folders. For example, if plan-1.json is in cluster 0, move it to clusterSet-0/cluster-0/plan-1.json
    for i in range(num_plans):
        plan = gpd.read_file(
            f"./{state}/ensemble-{ensembleId}/districts_reassigned/plan-{i+1}.json"
        )

        # create cluster folders
        makedirs(
            f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}/cluster-{y_kmeans[i]+1}",
            exist_ok=True,
        )

        # save plan into its respective cluster folder
        plan.to_file(
            f"./{state}/ensemble-{ensembleId}/clusterSet-{id+1}/cluster-{y_kmeans[i]+1}/plan-{i+1}.json",
            driver="GeoJSON",
        )

    return y_kmeans


if __name__ == "__main__":
    # start("AZ", 0)
    pass
