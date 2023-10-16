import maup
import geopandas
import matplotlib.pyplot as plt
from gerrychain import Graph, Partition

districts = geopandas.read_file("https://www2.census.gov/geo/tiger/TIGER2012/SLDU/tl_2012_25_sldu.zip")
units = geopandas.read_file("zip://./BG25.zip")

units.to_crs(districts.crs, inplace=True)
assignment = maup.assign(units, districts)

assignment.isna().sum()

units["SENDIST"] = assignment

graph = Graph.from_json("./Block_Groups/BG25.json")

graph.join(units, columns=["SENDIST"], left_index="GEOID10", right_index="GEOID10")

real_life_plan = Partition(graph, "SENDIST")

real_life_plan.plot(units, figsize=(10, 10), cmap="tab20")
plt.axis('off')
plt.show()