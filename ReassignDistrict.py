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

start_time = datetime.now()

"""
REQUIRED FILES:
1. 10 jsons in ./districts
"""


def reassign(arg):
    # open all the jsons in ./districts, and reassign district numbers (that means, update SLDL_DIST column) to match the district numbers of the first json based on its geometric similarity
    # save the new jsons into ./districts_reassigned

    original_plan = gpd.read_file(f"./districts/az_pl2020_sldl_{1000}.json")
    original_plan = original_plan.to_crs(32030)

    # print if the polygon is valid
    # print("original plan:\n", original_plan.geometry.is_valid)

    # original_plan["geometry"] = original_plan["geometry"].buffer(0)

    # recheck if the polygon is valid
    # print("recheck original plan:\n", original_plan.geometry.is_valid)

    """
    for i in range(2000, 11000, 1000):
    """
    new_plan = gpd.read_file("./districts/az_pl2020_sldl_" + str(arg) + ".json")
    new_plan = new_plan.to_crs(32030)

    print("For new plan", arg, ":")

    # for each district in new_plan, find the district in original_plan that has the most similar geometry

    matrix = np.zeros((len(new_plan), len(original_plan)))  # 30 x 30

    for district in new_plan["SLDL_DIST"].unique():
        # get the geometry of the current district in new_plan
        # print("i:", i, "district:", district)
        new_plan_district = new_plan.loc[new_plan["SLDL_DIST"] == district]
        # print("new plan district:\n", new_plan_district)

        # validate the geometry
        # print("new plan:\n", new_plan_district.geometry.is_valid)

        # recheck if the polygon is valid
        # print("recheck new plan:\n", new_plan_district.geometry.is_valid)

        # find intersection between the current district in new_plan and all the districts in original_plan
        for original_district in original_plan["SLDL_DIST"].unique():
            # print("j:", j)
            original_plan_district = original_plan.loc[
                original_plan["SLDL_DIST"] == original_district
            ]
            # print("original plan district:\n", original_plan_district)

            # validate the geometry
            # print("original plan:\n", original_plan_district.geometry.is_valid)

            # recheck if the polygon is valid
            # print("recheck original plan:\n", original_plan_district.geometry.is_valid)

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

            # print("similarity:", similarity)

            # print("intersection:\n", intersection)
            # print("area:\n", area)

            # save the area into the matrix if it is not itself
            if district != original_district:
                matrix[int(district) - 1][int(original_district) - 1] = similarity

    # print("matrix:\n", matrix)

    # find the highest similarity for each district in new_plan
    # print("max:\n", unravel_index(matrix.argmax(), matrix.shape))

    # initialize NEW_SLDL_DIST column
    new_plan["NEW_SLDL_DIST"] = 0

    while np.any(matrix):
        idx = unravel_index(matrix.argmax(), matrix.shape)
        # print("idx:", idx[0], idx[1])
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
            new_plan.loc[new_plan["SLDL_DIST"] == district, "NEW_SLDL_DIST"].values[0]
            == 0
        ):
            new_plan.loc[new_plan["SLDL_DIST"] == district, "NEW_SLDL_DIST"] = district

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
        "./districts_reassigned/az_pl2020_sldl_" + str(arg) + ".json",
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
    plt.savefig("./plots_reassigned/az_pl2020_sldl_" + str(arg) + ".png")


end_time = datetime.now()

print("Duration: {}".format(end_time - start_time))


if __name__ == "__main__":
    NUM_PROJECTED_PLANS = 10000
    # get number of cores

    NUM_PLANS_PER_CORE = math.ceil(NUM_PROJECTED_PLANS / mp.cpu_count())

    print("NUM_PLANS_PER_CORE:", NUM_PLANS_PER_CORE)

    """
    [1...NUM_CORES] folders be made in the units, plots, districts, districts_reassigned, plots_reassigned folders.
    Each folder will have NUM_PLANS_PER_CORE plans inside it.
    """

    with Pool(processes=9) as pool:
        pool.map(reassign, [x for x in range(2000, 11000, 1000)])
