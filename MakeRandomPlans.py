import ReComMaup
import ReComNoMaup
import ReassignDistrict
from os import makedirs
import sys

if __name__ == "__main__":
    state = sys.argv[1]

    # Configure directories
    if state in ["AZ", "LA", "NV"]:
        makedirs(f"{state}", exist_ok=True)

    # Generate random plans
    if state == "AZ":
        ReComNoMaup.start(state)
    elif state == "LA":
        ReComNoMaup.start(state)
    elif state == "NV":
        ReComMaup.start(state)
    else:
        print("Invalid state.")

    # Reassign districts
    if state in ["AZ", "LA", "NV"]:
        ReassignDistrict.start(state)

    pass
