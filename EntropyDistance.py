import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime

#how much two different districting plans "differ"
def ent_D_D(gdf, district_column1, district_column2, population_column):
    entropy = 0
    totalpop = gdf[population_column].sum()
    districts_intersections = gdf.dissolve(by=[district_column1,district_column2], aggfunc='sum')
    district2_populations = gdf.dissolve(by=district_column2, aggfunc='sum')[population_column]
    for i, row in districts_intersections.iterrows():
        if row[population_column] > 0:
            entropy += 1/totalpop*row[population_column]*np.log2(
                district2_populations[row.name[1]]/row[population_column]
            )
    return entropy

def entropydistance(a,b,ensemble_id) :
    districtlistA = pd.read_csv(f"./AZ/ensemble-{ensemble_id}/district_list/district_list-{a}.csv")
    districtlistB = pd.read_csv(f"./AZ/ensemble-{ensemble_id}/district_list/district_list-{b}.csv")
    planA = gpd.read_file(f"./AZ/ensemble-{ensemble_id}/units/plan-{a}.json")
    planB = pd.read_csv(f"./AZ/ensemble-{ensemble_id}/plandistrict/plandistrict-{b}.csv")
    dfA = planA[["PCTNUM", "SLDL_DIST", "Total_Population", "geometry"]]

    for i in dfA.index:
        dfA["SLDL_DIST"][i] = int(dfA["SLDL_DIST"][i])

    mergeA = dfA.merge(dfA.merge(districtlistA, how='left', on='SLDL_DIST', sort=False))
    mergeB = planB.merge(planB.merge(districtlistB, how='left', on='SLDL_DIST', sort=False))
    mergeA["SLDL_DIST_2"] = 0

    for i in mergeA.index:
        mergeA["SLDL_DIST_2"][i] = mergeB["NEW_SLDL_DIST"][i]

    return ent_D_D(mergeA, "NEW_SLDL_DIST", "SLDL_DIST_2", "Total_Population")