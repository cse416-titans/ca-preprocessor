import geopandas as gpd
from datetime import datetime
from os import makedirs
import json
import collections

if __name__ == "__main__":
    # open all json files in ./districts_reassigned and generate summary statistics in ./summary
    start_time = datetime.now()

    makedirs("summary", exist_ok=True)

    for i in range(2000, 11000, 1000):
        districts = gpd.read_file(f"./districts_reassigned/az_pl2020_sldl_{i}.json")

        # drop the geometry column
        districts = districts.drop(columns=["geometry"])

        districts.set_index("SLDL_DIST", drop=True, inplace=True)
        d = districts.to_dict(orient="index")

        od = collections.OrderedDict(sorted(d.items()))

        """
        TODO: Add other statistics, e.g., if it is opportunity district, if it is minority-majority district, etc.
        """

        # save the dictionary into a json
        with open(f"./summary/az_pl2020_sldl_{i}.json", "w") as outfile:
            json.dump(od, outfile, indent=4)
