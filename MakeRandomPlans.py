import ReComMaup
import ReComNoMaup

def start(state, num_cores, num_plans, ensembleId):
    # Generate random plans
    if state == "AZ":
        ReComNoMaup.start(state, num_cores, num_plans, ensembleId)
    elif state == "LA":
        ReComNoMaup.start(state, num_cores, num_plans, ensembleId)
    elif state == "NV":
        ReComNoMaup.start(state, num_cores, num_plans, ensembleId)
    else:
        print("Invalid state.")
