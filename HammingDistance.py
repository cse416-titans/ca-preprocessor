import pandas as pd
import geopandas as gpd
from datetime import datetime

def hammingdistance(a, b, ensemble_id):
    districtlistA = pd.read_csv(f"./AZ/ensemble-{ensemble_id}/district_list/district_list-{a}.csv")
    districtlistB = pd.read_csv(f"./AZ/ensemble-{ensemble_id}/district_list/district_list-{b}.csv")
    planA = pd.read_csv(f"./AZ/ensemble-{ensemble_id}/plandistrict/plandistrict-{a}.csv")
    planB = pd.read_csv(f"./AZ/ensemble-{ensemble_id}/plandistrict/plandistrict-{b}.csv")

    cur_time = datetime.now()
    mergeA = planA.merge(planA.merge(districtlistA, how="left", on="SLDL_DIST", sort=False))
    mergeB = planB.merge(planB.merge(districtlistB, how="left", on="SLDL_DIST", sort=False))
    cur_time = datetime.now()
    total = 0
    for i in mergeA.index:
        if mergeA["NEW_SLDL_DIST"][i] != mergeB["NEW_SLDL_DIST"][i]:
            # print("i: " + str(i) + " A: " + str(mergeA["NEW_SLDL_DIST"][i]) + " B: " + str(mergeB["NEW_SLDL_DIST"][i]))
            total += 1
    return total
