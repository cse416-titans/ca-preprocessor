import MakeClusters
import MakeRandomPlans
import ReassignDistrict

from os import makedirs
import sys

if __name__ == "__main__":
    state = sys.argv[1]

    num_cores = int(sys.argv[2])
    num_plans = int(sys.argv[3])

    # Configure directories
    makedirs(f"{state}", exist_ok=True)

    # Generate random plans (populate  district level geojson)
    MakeRandomPlans.start(state, num_cores, num_plans)

    # Reassign districts (populate reassigned district level geojson)
    ReassignDistrict.start(state, num_cores, num_plans)

    # Make clusters (find cluster points and make a folder structure)
    MakeClusters.start(state, num_cores, num_plans)
