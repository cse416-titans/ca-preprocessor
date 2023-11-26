import ReComMaup
import ReComNoMaup


def start(state, num_cores, num_plans):
    # Generate random plans
    if state == "AZ":
        ReComNoMaup.start(state, num_cores, num_plans)
    elif state == "LA":
        ReComNoMaup.start(state, num_cores, num_plans)
    elif state == "NV":
        ReComMaup.start(state, num_cores, num_plans)
    else:
        print("Invalid state.")

    """
    TODO: Rename files in order
    """
