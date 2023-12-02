import MakeClustersByDistanceMeasure


def start(state, num_cores, num_plans, ensembleId):
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
        MakeClustersByDistanceMeasure.start(state, 0, num_cores, num_plans, ensembleId)
        # MakeClustersByDistanceMeasure.start(state, 1, num_cores, num_plans, ensembleId)
        # MakeClustersByDistanceMeasure.start(state, 2, num_cores, num_plans, ensembleId)
    elif state == "LA":
        MakeClustersByDistanceMeasure.start(state, 0, num_cores, num_plans, ensembleId)
    elif state == "NV":
        MakeClustersByDistanceMeasure.start(state, 0, num_cores, num_plans, ensembleId)
    else:
        print("Invalid state.")
