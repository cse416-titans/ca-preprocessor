import pandas as pd
import geopandas as gpd


def hammingdistance(a, b):
    districtlistA = pd.read_csv(f"./AZ/district_list/district_list-{a}.csv")
    districtlistB = pd.read_csv(f"./AZ/district_list/district_list-{b}.csv")

    planA = gpd.read_file(f"./AZ/units/plan-{a}.json")
    planB = gpd.read_file(f"./AZ/units/plan-{b}.json")

    dfA = planA[["PCTNUM", "SLDL_DIST"]]
    dfB = planB[["PCTNUM", "SLDL_DIST"]]

    for i in dfA.index:
        dfA["SLDL_DIST"][i] = int(dfA["SLDL_DIST"][i])
        dfB["SLDL_DIST"][i] = int(dfB["SLDL_DIST"][i])

    mergeA = dfA.merge(dfA.merge(districtlistA, how="left", on="SLDL_DIST", sort=False))
    mergeB = dfB.merge(dfB.merge(districtlistB, how="left", on="SLDL_DIST", sort=False))

    total = 0
    for i in mergeA.index:
        if mergeA["NEW_SLDL_DIST"][i] != mergeB["NEW_SLDL_DIST"][i]:
            # print("i: " + str(i) + " A: " + str(mergeA["NEW_SLDL_DIST"][i]) + " B: " + str(mergeB["NEW_SLDL_DIST"][i]))
            total += 1

    return total
