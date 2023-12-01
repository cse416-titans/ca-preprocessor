import numpy as np
import cvxpy as cp
import networkx as nx
from typing import List, Dict
from gerrychain import Partition
from scipy.optimize import linear_sum_assignment
from networkx.linalg.graphmatrix import incidence_matrix

import pandas as pd
import geopandas as gpd
import numpy as np

from sklearn.manifold import MDS
from sklearn.cluster import KMeans

from datetime import datetime
from os import makedirs

import multiprocessing as mp
from multiprocessing import Pool, Manager, current_process

import math
from random import random

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
import maup
        
districtsA = gpd.read_file(f"./AZ/districts_reassigned/plan-2.json")
districtsB = gpd.read_file(f"./AZ/districts_reassigned/plan-3.json")

planA = gpd.read_file(f"./AZ/units/plan-2.json")
planB = gpd.read_file(f"./AZ/units/plan-3.json")

PlanA_Assignment = maup.assign(planA, districtsA)
PlanB_Assignment = maup.assign(planB, districtsB)

planA["new_dist"] = PlanA_Assignment
print(planA)

"""
print(PlanA_Assignment.compare(PlanB_Assignment))
        
data = PlanA_Assignment.compare(PlanB_Assignment)
data.to_csv("diff.csv")
"""