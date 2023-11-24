from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept

import pandas
import matplotlib.pyplot as plt

graph = Graph.from_json("./PA_VTDs.json")

print(graph)

election = Election("SEN12", {"Dem": "USS12D", "Rep": "USS12R"})

initial_partition = Partition(
    graph,
    assignment="CD_2011",
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("TOTPOP", alias="population"),
        "SEN12": election
    }
)

for district, pop in initial_partition["population"].items():
    print("District {}: {}".format(district, pop))


chain = MarkovChain(
    proposal=propose_random_flip,
    constraints=[single_flip_contiguous],
    accept=always_accept,
    initial_state=initial_partition,
    total_steps=1000
)

i=0
for partition in chain:
    if i>2:
        break
    dd = pandas.DataFrame(partition.graph.nodes(data=True))
    print(dd)
    i+=1

d_percents = [sorted(partition["SEN12"].percents("Dem")) for partition in chain]

data = pandas.DataFrame(d_percents)

a = [partition for partition in chain]

b = pandas.DataFrame(a[0]['SEN12'].percents('Dem'))

print(b)

initial_partition.plot(units, figsize=(10, 10), cmap="tab20")
plt.axis('off')
plt.show()

"""
ax = data.boxplot(positions=range(len(data.columns)))
plt.plot(data.iloc[0], "ro")

plt.show()
"""