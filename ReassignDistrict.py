import geopandas as gpd
import matplotlib.pyplot as plt
import warnings
from datetime import datetime
import numpy as np
from numpy import unravel_index
from polygonUtil import formatStr
import multiprocessing as mp
from multiprocessing import Pool
import math

warnings.filterwarnings("ignore")

"""
REQUIRED FILES:
1. jsons in ./districts
"""

NUM_CORES = 0
NUM_PROJECTED_PLANS = 0


def initWorker(state, num_cores, num_plans, ensembleId):
    global NUM_PROJECTED_PLANS_PER_CORE
    global NUM_CORES
    global stateAbbr
    global ensemble_id

    stateAbbr = state
    ensemble_id = ensembleId

    NUM_CORES = num_cores
    NUM_PROJECTED_PLANS = num_plans
    NUM_PROJECTED_PLANS_PER_CORE = math.ceil(NUM_PROJECTED_PLANS / NUM_CORES)


def reassign(arg):
    original_plan = gpd.read_file(
        f"./{stateAbbr}/ensemble-{ensemble_id}/districts/plan-{1}.json"
    )
    original_plan = original_plan.to_crs(32030)

    n = NUM_PROJECTED_PLANS_PER_CORE
    procId = arg + 1

    for x in range(n):
        fileId = (x + 1) + (procId - 1) * n

        new_plan = gpd.read_file(
            f"./{stateAbbr}/ensemble-{ensemble_id}/districts/plan-{fileId}.json"
        )
        new_plan = new_plan.to_crs(32030)

        print(f"For process {procId}, new_plan: {x}")

        # for each district in new_plan, find the district in original_plan that has the most similar geometry
        matrix = np.zeros((len(new_plan), len(original_plan)))  # 30 x 30

        for district in new_plan["SLDL_DIST"].unique():
            new_plan_district = new_plan.loc[new_plan["SLDL_DIST"] == district]

            # find intersection between the current district in new_plan and all the districts in original_plan
            for original_district in original_plan["SLDL_DIST"].unique():
                original_plan_district = original_plan.loc[
                    original_plan["SLDL_DIST"] == original_district
                ]

                intersection = gpd.overlay(
                    new_plan_district, original_plan_district, how="intersection"
                )

                area_difference = abs(
                    new_plan_district["geometry"].area.sum()
                    - original_plan_district["geometry"].area.sum()
                )

                perimeter_difference = abs(
                    new_plan_district["geometry"].length.sum()
                    - original_plan_district["geometry"].length.sum()
                )

                similarity = (
                    1e-5 * (intersection["geometry"].area.sum())
                    + 1e4 * (1 / area_difference)
                    + 1e4 * (1 / perimeter_difference)
                )

                matrix[int(district) - 1][int(original_district) - 1] = similarity

        new_plan["NEW_SLDL_DIST"] = 0

        while np.any(matrix):
            idx = unravel_index(matrix.argmax(), matrix.shape)
            dist = matrix[idx[0], idx[1]]

            # reassign new_plans idx[0]th district to original_plans idx[1]th district
            # if NEW_SLDL_DIST already had that district, then skip
            if (
                new_plan.loc[
                    new_plan["SLDL_DIST"] == formatStr(idx[0] + 1), "NEW_SLDL_DIST"
                ].values[0]
                == 0
            ):
                new_plan.loc[
                    new_plan["SLDL_DIST"] == formatStr(idx[0] + 1), "NEW_SLDL_DIST"
                ] = formatStr(idx[1] + 1)

            matrix[:, idx[1]] = 0
            matrix[idx[0], :] = 0

        # for all unassigned districts, just assign them whatever is left
        for district in new_plan["SLDL_DIST"].unique():
            if (
                new_plan.loc[new_plan["SLDL_DIST"] == district, "NEW_SLDL_DIST"].values[
                    0
                ]
                == 0
            ):
                new_plan.loc[
                    new_plan["SLDL_DIST"] == district, "NEW_SLDL_DIST"
                ] = district

        # check if unique
        print("unique:", new_plan["NEW_SLDL_DIST"])
        print("unique:", new_plan["NEW_SLDL_DIST"].is_unique)

        # save old-new district assignment pairs into a csv
        distlist = new_plan[["SLDL_DIST", "NEW_SLDL_DIST"]]
        distlist.to_csv(
            f"./{stateAbbr}/ensemble-{ensemble_id}/district_list/district_list-{fileId}.csv"
        )

        new_plan = new_plan.drop(columns=["SLDL_DIST"])
        new_plan = new_plan.rename(columns={"NEW_SLDL_DIST": "SLDL_DIST"})
        new_plan["geometry"] = new_plan["geometry"].to_crs(4326)

        new_plan.to_file(
            f"./{stateAbbr}/ensemble-{ensemble_id}/districts_reassigned/plan-{fileId}.json",
            driver="GeoJSON",
        )

        ax = new_plan.plot(column="SLDL_DIST", cmap="tab20")

        new_plan.apply(
            lambda x: ax.annotate(
                text=x["SLDL_DIST"], xy=x.geometry.centroid.coords[0], ha="center"
            ),
            axis=1,
        )

        plt.axis("off")
        plt.savefig(
            f"./{stateAbbr}/ensemble-{ensemble_id}/plots_reassigned/plan-{fileId}.png"
        )
        plt.close()


def start(state, num_cores, num_plans, ensembleId):
    start_time = datetime.now()

    NUM_PLANS = 20

    with Pool(
        initializer=initWorker,
        initargs=(state, num_cores, num_plans, ensembleId),
        processes=num_cores,
    ) as pool:
        pool.map(reassign, range(num_cores))
        pool.close()
        pool.join()

    end_time = datetime.now()

    print("Duration: {}".format(end_time - start_time))


if __name__ == "__main__":
    start()
