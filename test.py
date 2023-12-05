from OptimalTransport import Pair
from HammingDistance import hammingdistance
from EntropyDistance import entropydistance

import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import numpy as np

from sklearn.manifold import MDS
from sklearn.cluster import KMeans

from datetime import datetime
from os import makedirs

from multiprocessing import Pool, Manager, current_process

import math
from random import random

from gerrychain import GeographicPartition, Graph
from datetime import datetime

start_time = datetime.now()
ensemble_id = 1

districtsA = gpd.read_file(
    f"./AZ/ensemble-{ensemble_id}/units/plan-1.json"
)
graphA = Graph.from_geodataframe(districtsA)
districtsB = gpd.read_file(
    f"./AZ/ensemble-{ensemble_id}/units/plan-2.json"
    )
graphB = Graph.from_geodataframe(districtsB)

print(Pair(
    GeographicPartition(graphA, assignment="SLDL_DIST"),
    GeographicPartition(graphB, assignment="SLDL_DIST"),
).distance)

end_time = datetime.now()

print("Duration: ", end_time - start_time)