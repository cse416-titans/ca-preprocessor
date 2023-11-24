from OptimalTransport import Pair
import matplotlib.pyplot as plt
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election, graph)
from gerrychain.proposals import recom
from functools import partial
import pandas as pd
import geopandas as gpd

azgdf1 = gpd.read_file("az_pl2020_vtd_10.json")
azgdf2 = gpd.read_file("az_pl2020_vtd_100.json")

neighbors1 = Graph.from_geodataframe(azgdf1)

neighbors2 = Graph.from_geodataframe(azgdf2)


elections = [
    Election("PRED20", {"Dem": "G20PREDBID", "Rep": "G20PRERTRU"})
]

my_updaters = {"population": updaters.Tally("Total_Population", alias="population")}

election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

partition1 = GeographicPartition(neighbors1, assignment="SLDL_DIST", updaters=my_updaters)
partition2 = GeographicPartition(neighbors2, assignment="SLDL_DIST", updaters=my_updaters)

optPair = Pair(partition_a=partition1, partition_b=partition2)

print(optPair)
print(optPair._pairwise_distances)
print(optPair.distance)
print(optPair._get_pairwise_distances)