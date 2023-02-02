import pandas as pd
import re
import sqlalchemy as sa
import os
import datetime
import ingestors.ancillarydata
import ingestors.ancillarydatadetail
import ingestors.energy
import ingestors.rec

class ParseError(Exception):
    pass

class ExistingDataError(Exception):
    pass

class SQLError(Exception):
    pass

def storage(m):
    pass

def validate(f):
    # WARNING 24 hour clock needs to be used when supplying timestamp
    # validate file name (or its one we can normalize)
    # e.g. ForwardCurve_NYISO_2X16_20221209_010101.csv
    # curveType_iso_strip_curveDate.csv
    # curveType_iso_strip_curveDate_curveTime.csv
    # curveType_iso_strip_curveDate_cob.csv
    file_name_components_pattern = re.compile(".*/(.+?)_(.+?)_(.+?)_(.+?)_(.+)?.csv$") # len(4) , check windows users :(
    
    print(f"Checking file name {f}")
    matched = file_name_components = file_name_components_pattern.search(f)
    if matched == None:
        return ParseError(f"failed to parse {f} - regex")
    
    results = matched.groups() # 5 might be None if original name
    if len(results) != 5:
        return ParseError(f"failed to parse {f} - component count")

    (curveType, controlArea, strip, curveDate, issue) = results    
    curveType = os.path.basename(curveType).replace("Curve","")

    # add default value here for time, maybe not worth it, need to see how it flows
    timeComponent = None
    if issue is None:    
        timeComponent = "000000"
    else:
        timeStamp = issue[1:] # drop leading underscore; else fix regex above
        if timeStamp == "cob":
            timeComponent = "235959" # 24h clock, convert to last possible second so we can sort properly
        elif int(timeStamp):
            timeComponent = timeStamp
        else:
            return ParseError(f"failed to parse {f} - time component")

    timestamp = datetime.datetime.strptime(curveDate+timeComponent, "%Y%m%d%H%M%S")
    return TLE_Meta(f, curveType, controlArea, strip, timestamp)

# def scd_2_panda():
#     database = os.environ["DATABASE"]
#     pgpassword = os.environ["PGPASSWORD"]
#     pguser = os.environ["PGUSER"]
#     engine = sa.create_engine(f"postgresql://{pguser}:{pgpassword}@{database}:5432/trueprice",
#     #connect_args={'options': '-csearch_path=trueprice'}
#     )

#     # new_data = receive new data
#     # if new_data not in current_db -> insert new to current_db (if fails???) // save data to local disk before next step?
#     # else new_data in current_db -> copy existing_data to history_db then update existing_data with new_data (if fails???) // save data to local disk before next step?

#     r1 = pd.read_sql(sa.text("SELECT * FROM test_data"), engine) # current
#     r2 = pd.read_sql(sa.text("SELECT * FROM test_data_history"), engine) # history
    
#     r3 = r2.join(r1, on="id", )
#     print(r3)

# # for potential refactor
# ca = {
#     "nyiso": {
#         "table": "trueprice.nyiso_forwardcurve",
#         "zones": []
#     },
#     "miso": {
#         "table": "trueprice.miso_forwardcurve",
#         "zones": []
#     },
#     "pjm": {
#         "table": "trueprice.pjm_forwardcurve",
#         "zones": []
#     },
#     "isone": {
#         "table": "trueprice.isone_forwardcurve",
#         "zones": []
#     },
#     "ercot": {
#         "table": "trueprice.ercot_forwardcurve",
#         "zones": ["north_amount","houston_amount","south_amount","west_amount"],
#     }
# }

def validate_api(m):
    None

class TLE_Meta:
    def __init__(self, fileName, curveType, controlArea, strip, curveTimestamp):
        self.fileName = fileName
        self.curveType = curveType.lower()
        self.controlArea = controlArea.lower()
        self.strip = strip.lower()
        self.curveStart = curveTimestamp
    
    def snake_timestamp(self):
        return self.curveStart.strftime("%Y_%m_%d_%H_%M_%S")
    
def process(files, steps):
    meta = None

    # validate
    valid = []
    for f in files:
        meta = steps["v"](f)
        if meta is None or isinstance(meta, ParseError):
            return meta # all files must pass, in case systematic errors
        else:
            valid.append(meta)

    # storage
    # add sha later
    for m in valid:
        result = steps["s"](m) # store before we place in db
        if result is not None :
            return result

    # insert db / api check each as we go (need to find way to redo/short-circuit/single file, etc.)
    for m in valid:
        result = steps["i"](m) # insert/update db
        if result is not None:
            return result
        result = steps["va"](m) # validate data made it to db via api
        if result is not None:
            return result

    return None

def call_ingestor(file):
    import sys
    print(f"Processing {file}", file=sys.stderr) # flask capture stdout so need to use stderr for now, fix later
    files = [file]
    result = None
    if re.search("forward", file, re.IGNORECASE):
        result = process(files, {"v":validate, "s":storage, "i":ingestors.energy.ingestion, "va": validate_api})
    elif re.search("ancillarydatadetails", file, re.IGNORECASE):
        result = process(files, {"v":validate, "s":storage, "i":ingestors.ancillarydatadetail.ingestion, "va": validate_api})
    elif re.search("ancillarydata", file, re.IGNORECASE):
        result = process(files, {"v":validate, "s":storage, "i":ingestors.ancillarydata.ingestion, "va": validate_api})
    else:
        print("Shouldn't be here")
        return

    if result is not None:
        print(f"Ingestion Failed: {result}")
    else:
        print("Ingestion Succeeded")

    print("Finished Ingestion")


if __name__ == "__main__":
    print("Starting")

    files = [
#        "./buildContext/data/ForwardCurve_NYISO_2X16_20221209.csv", # strip 1 assuming no HHMMSS is 000000 (midnight)
#        "./buildContext/data/ForwardCurve_NYISO_5X16_20221209.csv", # strip 2
        #"./buildContext/data/ForwardCurve_NYISO_7X8_20221209.csv", # new 
        #"./buildContext/data/ForwardCurve_NYISO_7X8_20221209_121212.csv", # strip 3 interday HHMMSS
        #"./buildContext/data/ForwardCurve_NYISO_7X8_20221209_cob.csv", # strip 3 cob
        #"./buildContext/data/ForwardCurve_NYISO_7X8_20221209_121211.csv", # sneak old past cob
        #"./buildContext/data/ForwardCurve_NYISO_7X8_20221209_121212.csv", # strip 3 interday (should not do it)
        #"./buildContext/data/ForwardCurve_NYISO_5X16_20221209.csv", # trying new strip same date
        # "./buildContext/data/ForwardCurve_NYISO_5X16_20230109_084700.csv", # new days data
        #"./buildContext/data/ForwardCurve_MISO_5X16_20230109_084700.csv", # refactoring for MISO from NYISO only
        #"./buildContext/data/ForwardCurve_ISONE_5X16_20230109_084700.csv",
        #"./buildContext/data/ForwardCurve_ERCOT_5X16_20230109_084700.csv",
        # "./buildContext/data/ForwardCurve_PJM_5x16_20230109_084700.csv",
    ]

    # v == validate files names/shape
    # s == store in AWS s3
    # i == ingest into postgres
    # va == validate the data can be retrieved via API
    result = process(files, {"v":validate, "s":storage, "i":ingestors.energy.ingestion, "va": validate_api})
    if result is not None:
        print(f"Ingestion Failed: {result}")
    else:
        print("Ingestion Succeeded")

    print("Finished Ingestion")
else:
    print("Running ingestor via API {}", __name__)