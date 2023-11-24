import pandas as pd
import geopandas as gpd
import shapely
import json
import csv
import numpy as np
import geojson

azgdf = gpd.read_file("az_gen_20_prec.shp")
new_azgdf = azgdf[['PCTNUM','PRECINCTNA', 'SLDL_DIST', 'G20PREDBID', 'G20PRERTRU', 'geometry']]

print(new_azgdf)

azcsv = pd.read_csv("mgggaz.csv")
new_azcsv = azcsv[['CODE','TOTPOP','NH_WHITE','NH_BLACK','NH_AMIN','NH_ASIAN','HISP','NH_OTHER']]
renamedazcsv = new_azcsv.rename(columns={'CODE' : 'PCTNUM', 'TOTPOP' : 'Total_Population', 'NH_WHITE' : 'White', 'NH_BLACK' : 'Black', 'NH_AMIN' : 'American_Indian', 'NH_ASIAN' : 'Asian', 'HISP' : 'Hispanic', 'NH_OTHER' : 'Other_Race'})


merged_az = new_azgdf.merge(renamedazcsv, on = 'PCTNUM')

crsaz = merged_az.to_crs(3857)
print(crsaz)

crsaz.to_file('azjson.json')