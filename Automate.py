import MakeClusters
import MakeRandomPlans
import ReassignDistrict
import MakePlanSummary

from os import makedirs
import sys

if __name__ == "__main__":
    num_cores = int(sys.argv[1])

    for state in ["AZ", "LA"]:
        makedirs(f"{state}", exist_ok=True)
        ensembleId = 0
        for num_plans in [5, 7]:
            ensembleId += 1
            makedirs(f"{state}/ensemble-{ensembleId}", exist_ok=True)

            print(f"state: {state}, num_plans: {num_plans}, ensembleId: {ensembleId}")

            makedirs(f"{state}/ensemble-{ensembleId}", exist_ok=True)
            makedirs(f"{state}/ensemble-{ensembleId}/units", exist_ok=True)
            makedirs(f"{state}/ensemble-{ensembleId}/plots", exist_ok=True)
            makedirs(f"{state}/ensemble-{ensembleId}/districts", exist_ok=True)
            makedirs(
                f"{state}/ensemble-{ensembleId}/districts_reassigned", exist_ok=True
            )
            makedirs(f"{state}/ensemble-{ensembleId}/plots_reassigned", exist_ok=True)
            makedirs(f"{state}/ensemble-{ensembleId}/district_list", exist_ok=True)
            makedirs(f"{state}/ensemble-{ensembleId}/summary", exist_ok=True)

            # Generate random plans (populate  district level geojson)
            MakeRandomPlans.start(state, num_cores, num_plans, ensembleId)

            # Reassign districts (populate reassigned district level geojson)
            ReassignDistrict.start(state, num_cores, num_plans, ensembleId)

            # Make summary json
            MakePlanSummary.start(state, num_plans, ensembleId)

            # Make clusters (find cluster points and make a folder structure)
            MakeClusters.start(state, num_cores, num_plans, ensembleId)
