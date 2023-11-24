import geopandas as gpd
import matplotlib.pyplot as plt

import warnings

from datetime import datetime

warnings.filterwarnings("ignore")

start_time = datetime.now()

"""
REQUIRED FILES:
1. 10 jsons in ./districts
"""

# open all the jsons in ./districts, and reassign district numbers (that means, update SLDL_DIST column) to match the district numbers of the first json based on its geometric similarity
# save the new jsons into ./districts_reassigned

original_plan = gpd.read_file("./districts/az_pl2020_sldl_10.json")
original_plan = original_plan.to_crs(32030)

# print if the polygon is valid
# print("original plan:\n", original_plan.geometry.is_valid)

# original_plan["geometry"] = original_plan["geometry"].buffer(0)

# recheck if the polygon is valid
# print("recheck original plan:\n", original_plan.geometry.is_valid)

for i in range(20, 110, 10):
    new_plan = gpd.read_file("./districts/az_pl2020_sldl_" + str(i) + ".json")
    new_plan = new_plan.to_crs(32030)

    print("For new plan", i, ":")

    # for each district in new_plan, find the district in original_plan that has the most similar geometry
    taken = []

    for district in new_plan["SLDL_DIST"].unique():
        # get the geometry of the current district in new_plan
        # print("i:", i, "district:", district)
        new_plan_district = new_plan.loc[new_plan["SLDL_DIST"] == district]
        # print("new plan district:\n", new_plan_district)

        # validate the geometry
        # print("new plan:\n", new_plan_district.geometry.is_valid)

        # recheck if the polygon is valid
        # print("recheck new plan:\n", new_plan_district.geometry.is_valid)

        # find the district in original_plan that has the most similar geometry
        max_similarity = 0
        max_similarity_district = None
        for original_district in original_plan["SLDL_DIST"].unique():
            if original_district in taken:
                continue

            # get the geometry of the current district in original_plan
            original_plan_district = original_plan.loc[
                original_plan["SLDL_DIST"] == original_district
            ]

            # print("original plan district:\n", original_plan_district)

            # calculate the overlapped area between the two districts
            intersection = gpd.overlay(
                new_plan_district, original_plan_district, how="intersection"
            )

            # calculate similarity based on those two factors

            similarity = (
                intersection["geometry"].area.sum()
                / new_plan_district["geometry"].area.sum()
            )

            # update the max_similarity if necessary
            if similarity > max_similarity and similarity > 0:
                max_similarity = similarity
                max_similarity_district = original_district

        # update the district number of the current district in new_plan
        if max_similarity_district is None:
            print("no max similarity district found for district", district)
        else:
            new_plan.loc[
                new_plan["SLDL_DIST"] == district, "NEW_SLDL_DIST"
            ] = max_similarity_district

        taken.append(max_similarity_district)

        print(
            "for district",
            new_plan_district["SLDL_DIST"].iloc[0],
            ", max similarity district:",
            max_similarity_district,
        )

    # check if unique
    print("unique:", new_plan["NEW_SLDL_DIST"].is_unique)

    # drop the old SLDL_DIST column
    new_plan = new_plan.drop(columns=["SLDL_DIST"])

    # rename the NEW_SLDL_DIST column to SLDL_DIST
    new_plan = new_plan.rename(columns={"NEW_SLDL_DIST": "SLDL_DIST"})

    # revert its crs back to 4326
    new_plan["geometry"] = new_plan["geometry"].to_crs(4326)

    # save the new_plan into ./districts_reassigned
    new_plan.to_file(
        "./districts_reassigned/az_pl2020_sldl_" + str(i) + ".json", driver="GeoJSON"
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
    plt.savefig("./plots_reassigned/az_pl2020_sldl_" + str(i) + ".png")


end_time = datetime.now()

print("Duration: {}".format(end_time - start_time))
