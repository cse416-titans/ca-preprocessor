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
1. 10 jsons in ./districts
"""

NUM_CORES = 10


def initWorker():
    global NUM_PROJECTED_PLANS_PER_CORE
    global NUM_CORES

    NUM_PROJECTED_PLANS = 20
    NUM_PROJECTED_PLANS_PER_CORE = math.ceil(NUM_PROJECTED_PLANS / NUM_CORES)


def reassign(arg):
    start_time = datetime.now()

    # open all the jsons in ./districts, and reassign district numbers (that means, update SLDL_DIST column) to match the district numbers of the first json based on its geometric similarity
    # save the new jsons into ./districts_reassigned

    original_plan = gpd.read_file(f"./districts/az_pl2020_sldl_{1}_{0}.json")
    original_plan = original_plan.to_crs(32030)

    """
    for i in range(2000, 11000, 1000):
    """

    n = NUM_PROJECTED_PLANS_PER_CORE
    procId = arg + 1

    for x in range(n):
        new_plan = gpd.read_file(f"./districts/az_pl2020_sldl_{procId}_{x}.json")
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

                # find the intersection between the two districts
                intersection = gpd.overlay(
                    new_plan_district, original_plan_district, how="intersection"
                )

                # calculate the area difference between the two districts
                area_difference = abs(
                    new_plan_district["geometry"].area.sum()
                    - original_plan_district["geometry"].area.sum()
                )

                # calculate perimeter difference between the two districts
                perimeter_difference = abs(
                    new_plan_district["geometry"].length.sum()
                    - original_plan_district["geometry"].length.sum()
                )

                # calculate similarity based on those two factors
                similarity = (
                    1e-5 * (intersection["geometry"].area.sum())
                    + 1e4 * (1 / area_difference)
                    + 1e4 * (1 / perimeter_difference)
                )

                # save the area into the matrix
                matrix[int(district) - 1][int(original_district) - 1] = similarity

        # initialize NEW_SLDL_DIST column
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

            # also empty its swap location
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

        # drop the old SLDL_DIST column
        new_plan = new_plan.drop(columns=["SLDL_DIST"])

        # rename the NEW_SLDL_DIST column to SLDL_DIST
        new_plan = new_plan.rename(columns={"NEW_SLDL_DIST": "SLDL_DIST"})

        # revert its crs back to 4326
        new_plan["geometry"] = new_plan["geometry"].to_crs(4326)

        # save the new_plan into ./districts_reassigned
        new_plan.to_file(
            f"./districts_reassigned/az_pl2020_sldl_{procId}_{x}.json",
            driver="GeoJSON",
        )

        # also save its plot
        ax = new_plan.plot(column="SLDL_DIST", cmap="tab20")

        new_plan.apply(
            lambda x: ax.annotate(
                text=x["SLDL_DIST"], xy=x.geometry.centroid.coords[0], ha="center"
            ),
            axis=1,
        )

        plt.axis("off")
        plt.savefig(f"./plots_reassigned/az_pl2020_sldl_{procId}_{x}.png")
        plt.close()

    end_time = datetime.now()

    print("Duration: {}".format(end_time - start_time))


def start():
    NUM_PLANS = 20

    """
    [1...NUM_CORES] folders be made in the units, plots, districts, districts_reassigned, plots_reassigned folders.
    Each folder will have NUM_PLANS_PER_CORE plans inside it.
    """

    with Pool(initializer=initWorker, processes=NUM_CORES) as pool:
        pool.map(reassign, range(NUM_CORES))


if __name__ == "__main__":
    start()
