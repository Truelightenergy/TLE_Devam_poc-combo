import pandas as pd
import re

state_machine = {} # maybe use to track validity of process, e.g check valid file names, then format, then size, etc.

class ParseError(Exception):
    pass

def upload_to_aws_s3():
    pass

def forwardcurve_ingestion():
    files = ["ForwardCurve_NYISO_2X16_20221209.csv",
    "ForwardCurve_NYISO_5X16_20221209.csv",
    "ForwardCurve_NYISO_7X8_20221209.csva"]

    # ForwardCurve_NYISO_2X16_20221209.csv
    # curveType_iso_strip_curveDate.csv
    file_name_components_pattern = re.compile("(.+)_(.+)_(.+)_(.+).csv$") # len(4)

    for f in files:
        print(f"Checking File {f}")        
        # "ForwardCurve_NYISO_2X16_20221209.csv"
        matched = file_name_components = file_name_components_pattern.search(f)
        if matched == None:
            return
        
        results = matched.group(1,2,3,4) 
        if len(results) == 4:
                print(results)

        csv = pd.read_csv(f, header=4, nrows=1) # acts as context manager
        print(csv)

if __name__ == "__main__":
    print("Starting")
    forwardcurve_ingestion()
    print("Finished")
else:
    print("not a library: {}", __name__)