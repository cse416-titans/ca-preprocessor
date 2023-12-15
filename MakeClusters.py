import MakeClustersByDistanceMeasure


def start(state, num_cores, num_plans, ensembleId):
    if not state in ["AZ", "LA", "NV"]:
        print("Invalid state.")
        exit()
    """
    0: Hamming clusters
    1: Entropy clusters
    2: Optimal transport clusters
    """
    # Generate random plans
    for cluster_id in [0, 1, 2]:
        if state == "AZ":
            MakeClustersByDistanceMeasure.start(
                state, cluster_id, num_cores, num_plans, ensembleId
            )
        elif state == "LA":
            MakeClustersByDistanceMeasure.start(
                state, cluster_id, num_cores, num_plans, ensembleId
            )
        elif state == "NV":
            MakeClustersByDistanceMeasure.start(
                state, cluster_id, num_cores, num_plans, ensembleId
            )
        else:
            print("Invalid state.")
