import matplotlib.pyplot as plt
from gerrychain import (
    GeographicPartition,
    Partition,
    Graph,
    MarkovChain,
    proposals,
    updaters,
    constraints,
    accept,
    Election,
)
from gerrychain.proposals import recom
from functools import partial
import pandas as pd
import geopandas as gpd

azgdf = gpd.read_file("azjson.json")

neighbors = Graph.from_geodataframe(azgdf)

elections = [Election("PRED20", {"Dem": "G20PREDBID", "Rep": "G20PRERTRU"})]

my_updaters = {"population": updaters.Tally("Total_Population", alias="population")}

election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

initial_partition = GeographicPartition(
    neighbors, assignment="SLDL_DIST", updaters=my_updaters
)

ideal_population = sum(initial_partition["population"].values()) / len(
    initial_partition
)

for district, pop in initial_partition["population"].items():
    print("District {}: {}".format(district, pop))

# print(initial_partition)
# print(ideal_population)

proposal = partial(
    recom,
    pop_col="Total_Population",
    pop_target=ideal_population,
    epsilon=0.1,
    node_repeats=2,
)

compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]), 2 * len(initial_partition["cut_edges"])
)

pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.10)

chain = MarkovChain(
    proposal=proposal,
    constraints=[pop_constraint, compactness_bound],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=1000,
)

data = pd.DataFrame(sorted(partition["PRED20"].percents("Dem")) for partition in chain)

# print(data)

i = 0
for partition in chain:
    # save graph into json
    partition.graph.to_json("./graph/azjson" + str(i) + ".json")
    i += 1
    if i > 50:
        break

graph_new = Graph.from_json("./graph/azjson40.json")
plan_new = Partition(graph_new, "SLDL_DIST")
plan_new.plot(azgdf, figsize=(10, 10), cmap="tab20")
plt.axis("off")
plt.show()

"""
i = 0
for partition in chain:
    print("i: ", i)
    partition.plot(azgdf, figsize=(10, 10), cmap="tab20")
    plt.axis("off")
    plt.savefig("./fig/azjson" + str(i) + ".png")
    print("saved ", i)
    i += 1
"""
