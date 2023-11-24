from OptimalTransport import Pair
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
    graph,
)
from gerrychain.proposals import recom
from functools import partial
import pandas as pd
import geopandas as gpd

azgdf1 = gpd.read_file("./units/az_pl2020_vtd_1000.json").to_crs(32030)
azgdf2 = gpd.read_file("./units/az_pl2020_vtd_10000.json").to_crs(32030)

neighbors1 = Graph.from_geodataframe(azgdf1)

neighbors2 = Graph.from_geodataframe(azgdf2)


partition1 = GeographicPartition(neighbors1, assignment="SLDL_DIST")
partition2 = GeographicPartition(neighbors2, assignment="SLDL_DIST")

optPair = Pair(partition_a=partition1, partition_b=partition2)

print(optPair)
print(optPair._pairwise_distances)
print(optPair.distance)
print(optPair._get_pairwise_distances)
