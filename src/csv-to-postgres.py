import pandas as pd
import re

class ParseError(Exception):
    pass

def storage(f, r):
    pass

def validate(f):
    # ForwardCurve_NYISO_2X16_20221209.csv
    # curveType_iso_strip_curveDate.csv
    file_name_components_pattern = re.compile("(.+)_(.+)_(.+)_(.+).csv$") # len(4)
    
    print(f"Checking file name {f}")        
    # "ForwardCurve_NYISO_2X16_20221209.csv"
    matched = file_name_components = file_name_components_pattern.search(f)
    if matched == None:
        return ParseError(f"failed to parse {f}")
    
    results = matched.group(1,2,3,4) 
    if len(results) != 4:
        return ParseError(f"failed to parse {f}")

    return results

def ingestion(f, r):
    csv = pd.read_csv(f, header=4, nrows=1) # acts as context manager
    print(csv)
    None

def validate_api(f, r):
    None
    
def process(files, steps):
    components = None

    # validate
    for f in files:
        components = steps["v"](f)
        if components is None or isinstance(components, ParseError):
            return components # all files must pass, in case systematic errors

    # store
    for f in files:
        result = steps["s"](f, components) # store before we place in db
        if result is not None :
            return result

    # insert db / api check each as we go (need to find way to redo/short-circuit/single file, etc.)
    for f in files:    
        result = steps["i"](f, components) # insert/update db
        if result is not None:
            return result
        result = steps["va"](f, components) # validate data in db via api
        if result is not None:
            return result

    return None

if __name__ == "__main__":
    print("Starting")

    files = [
        "ForwardCurve_NYISO_2X16_20221209.csv",
        "ForwardCurve_NYISO_5X16_20221209.csv",
        "ForwardCurve_NYISO_7X8_20221209.csv"
    ]

    # v == validate files names/shape
    # s == store in AWS s3
    # i == ingest into postgres
    # va == validate the data can be retrieved via API
    result = process(files, {"v":validate, "s":storage, "i":ingestion, "va": validate_api})
    if result is not None:
        print("Failed")
    else:
        print("Succeeded")

    print("Finished")
else:
    print("Not a module {}", __name__)