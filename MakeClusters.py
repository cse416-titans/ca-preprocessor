import MakeOptimalTransportClusters


def start(state, num_cores, num_plans):
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
        MakeOptimalTransportClusters.start(state, 0, num_cores, num_plans)
        # MakeHammingClusters.start(state, 1)
        # MakeEntropyClusters.start(state, 2)
    elif state == "LA":
        MakeOptimalTransportClusters.start(state, 0, num_cores, num_plans)
    elif state == "NV":
        MakeOptimalTransportClusters.start(state, 0, num_cores, num_plans)
    else:
        print("Invalid state.")
