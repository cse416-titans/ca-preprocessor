import pandas as pd
import geopandas as gpd

from os import makedirs

from datetime import datetime
import multiprocessing as mp
from multiprocessing import Pool, Manager
import math

# default values
NUM_CORES = 0
NUM_PROJECTED_PLANS = 0

def initWorker(state, num_cores, num_plans, ensembleId):
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
    ensemble_id = ensembleId

    NUM_CORES = num_cores
    NUM_PLANS = num_plans
    NUM_COMPARISON = NUM_PLANS * NUM_PLANS / 2
    NUM_COMPARISON_PER_CORE = math.ceil(NUM_COMPARISON / NUM_CORES)

    queue_core = [[] for _ in range(NUM_CORES)]

    for i in range(NUM_PLANS):
        queue_core[i % NUM_CORES].append(i)

def makeDistrictNumbering(arg):
    queue = queue_core[arg]

    for i in range(len(queue)):
        print("i: ", i, ", queue[i]: ", queue[i])
        plan = gpd.read_file(f"./AZ/ensemble-{ensemble_id}/units/plan-{queue[i]+1}.json")
        pland = plan[["PCTNUM", "SLDL_DIST"]]
        pland["SLDL_DIST"] = pland["SLDL_DIST"].astype(int)
        pland.to_csv(f"./{stateAbbr}/ensemble-{ensemble_id}/plandistrict/plandistrict-{queue[i]+1}.csv")

def start(state, num_cores, num_plans, ensembleId):
    start_time = datetime.now()

    makedirs(f"./{state}/ensemble-{ensembleId}/plandistrict", exist_ok=True)

    with Pool(
        initializer=initWorker,
        initargs=(state, num_cores, num_plans, ensembleId),
        processes=num_cores,
    ) as pool:
        result = pool.map(makeDistrictNumbering, range(num_cores))
        pool.close()
        pool.join()

    end_time = datetime.now()

    print("Duration: ", end_time - start_time)

if __name__ == "__main__":
    start("AZ", 8, 16, 1)
