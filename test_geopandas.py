import geopandas
import maup
import matplotlib.pyplot as plt

districts = geopandas.read_file("pa_sldu_adopted_2022.zip")
units = geopandas.read_file("PA.zip")

units.to_crs(districts.crs, inplace=True)
assignment = maup.assign(units, districts)

sum = assignment.isna().sum()

print(sum)