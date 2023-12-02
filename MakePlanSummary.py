import geopandas as gpd
from datetime import datetime
from os import makedirs
import json
import collections


def start(state, num_plans, ensembleId):
    # open all json files in ./districts_reassigned and generate summary statistics in ./summary
    start_time = datetime.now()

    for i in range(1, num_plans + 1):
        districts = gpd.read_file(
            f"{state}/ensemble-{ensembleId}/districts_reassigned/plan-{i}.json"
        )

        # drop the geometry column
        districts = districts.drop(columns=["geometry"])

        districts.set_index("SLDL_DIST", drop=True, inplace=True)
        d = districts.to_dict(orient="index")

        od = collections.OrderedDict(sorted(d.items()))

        """
        TODO: Add other statistics, e.g., if it is opportunity district, if it is minority-majority district, etc.
        """

        # save the dictionary into a json
        with open(
            f"{state}/ensemble-{ensembleId}/summary/plan-{i}-summary.json", "w"
        ) as outfile:
            json.dump(od, outfile, indent=4)

    end_time = datetime.now()
    print("Duration: {}".format(end_time - start_time))
