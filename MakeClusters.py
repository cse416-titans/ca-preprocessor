import MakeOptimalTransportClusters
from os import makedirs
import sys

if __name__ == "__main__":
    state = sys.argv[1]

    # Configure directories
    if not state in ["AZ", "LA", "NV"]:
        print("Invalid state.")
        exit()

    """
    0: Optimal transport clusters
    1: Hamming clusters
    2: Entropy clusters
    """

    # Generate random plans
    if state == "AZ":
        MakeOptimalTransportClusters.start(state, 0)
        # MakeHammingClusters.start(state, 1)
        # MakeEntropyClusters.start(state, 2)
    elif state == "LA":
        MakeOptimalTransportClusters.start(state, 0)
    elif state == "NV":
        MakeOptimalTransportClusters.start(state, 0)
    else:
        print("Invalid state.")
