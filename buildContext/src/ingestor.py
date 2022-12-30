import pandas as pd
import re
import sqlalchemy as sa
import os
import datetime

class ParseError(Exception):
    pass

def storage(m):
    pass

def validate(f):
    # e.g. ForwardCurve_NYISO_2X16_20221209_010101.csv
    # curveType_iso_strip_curveDate.csv
    # curveType_iso_strip_curveDate_curveTime.csv
    # curveType_iso_strip_curveDate_cob.csv
    file_name_components_pattern = re.compile("(.+?)_(.+?)_(.+?)_(.+?)(_.+)?.csv$") # len(4)
    
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
            timeComponent = "115959" # convert to last possible second so we can sort properly
        elif int(timeStamp):
            timeComponent = timeStamp
        else:
            return ParseError(f"failed to parse {f} - time component")

    timestamp = datetime.datetime.strptime(curveDate+timeComponent, "%Y%m%d%H%M%S")
    return TLE_Meta(f, curveType, controlArea, strip, timestamp)

def scd_2_panda():
    database = os.environ["DATABASE"]
    pgpassword = os.environ["PGPASSWORD"]
    pguser = os.environ["PGUSER"]
    engine = sa.create_engine(f"postgresql://{pguser}:{pgpassword}@{database}:5432/trueprice",
    #connect_args={'options': '-csearch_path=trueprice'}
    )

    # new_data = receive new data
    # if new_data not in current_db -> insert new to current_db (if fails???) // save data to local disk before next step?
    # else new_data in current_db -> copy existing_data to history_db then update existing_data with new_data (if fails???) // save data to local disk before next step?

    r1 = pd.read_sql(sa.text("SELECT * FROM test_data"), engine) # current
    r2 = pd.read_sql(sa.text("SELECT * FROM test_data_history"), engine) # history
    
    r3 = r2.join(r1, on="id", )
    print(r3)

def ingestion(m):
    # using file name instead of rows to infer things like control zone and strip
    # this assumes the headers are like this:
    # Control Area	NYISO	NYISO	NYISO	NYISO	NYISO	NYISO	NYISO	NYISO	NYISO	NYISO	NYISO
    # ZoneID	28	29	30	31	32	33	34	35	36	37	38
    # Zone	ZONE A	ZONE B	ZONE C	ZONE D	ZONE E	ZONE F	ZONE G	ZONE H	ZONE I	ZONE J	ZONE K
    # Month	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE	FWD CURVE
    # 12/1/22	$54.42 	$54.42 	$55.47 	$52.99 	$49.77 	$98.78 	$84.39 	$83.88 	$81.92 	$89.62 	$89.39 
    # 1/1/23	$78.26 	$89.19 	$84.10 	$81.02 	$71.02 	$229.99 	$207.18 	$195.14 	$198.00 	$203.89 	$203.40 
    # ...
    # WARNING the provided CSV has many empty rows which are not skipped because they are empty strings
    date_cols = ['Zone']
    df = pd.read_csv(m.fileName, header=[2], skiprows=(3,3), dtype={
        'Zone': str, # Month aka Zone due to bad header
        # 'Zone A': pd.Float64Dtype, # ask guys on precision https://beepscore.com/website/2018/10/12/using-pandas-with-python-decimal.html
# ...
        # 'Zone K': pd.Float64Dtype
    }, parse_dates=date_cols).dropna() # acts as context manager
    df[df.columns[1:]] = df[df.columns[1:]].replace('[\$,]', '', regex=True).astype(float) # see warning on Float64Dtype, this removes money and converts to float
#    print(df)
#    print(len(df.index))
#    print(df.dtypes)

    """
    \c trueprice
    CREATE DATABASE trueprice;

        create table nyiso_forwardcurve ( -- history table differs
        id serial PRIMARY KEY,
        strip varchar(4), -- 7X8, 2X16, 7X24, etc. maybe enum one day
        curveStart TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54-05', -- per file name (sans tz)
        zone_a_amount numeric(12,8), -- varies by iso, unclear best approach, single table or per iso table
        zone_b_amount numeric(12,8),
        zone_c_amount numeric(12,8),
        zone_d_amount numeric(12,8), 
        zone_e_amount numeric(12,8),     
        zone_f_amount numeric(12,8), 
        zone_g_amount numeric(12,8),
        zone_h_amount numeric(12,8),
        zone_i_amount numeric(12,8), 
        zone_j_amount numeric(12,8),     
        zone_k_amount numeric(12,8)
        );

        -- old data
        -- union old and new data for all data (versus is_current column)
        create table nyiso_forwardcurve_history ( -- current table differs
        id serial, -- not primary, this is fk to nyiso_forwardcurve
        strip varchar(4), -- 7X8, 2X16, 7X24, etc. maybe enum one day
        curveStart TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54-05', -- per original file name
        curveEnd TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54-05', -- per new file name
        zone_a_amount numeric(12,8), -- varies by iso, unclear best approach, single table or per iso table
        zone_b_amount numeric(12,8),
        zone_c_amount numeric(12,8),
        zone_d_amount numeric(12,8), 
        zone_e_amount numeric(12,8),     
        zone_f_amount numeric(12,8), 
        zone_g_amount numeric(12,8),
        zone_h_amount numeric(12,8),
        zone_i_amount numeric(12,8), 
        zone_j_amount numeric(12,8),     
        zone_k_amount numeric(12,8)
        );
    """

    # 
    # if data in current -> backup
    # if not in current -> insert current
    #

    #
    # # what is "current data"
    # curve & iso & strip & date (not price as it changes)
    #

    database = os.environ["DATABASE"] if "DATABASE" in os.environ else "localhost"
    pgpassword = os.environ["PGPASSWORD"] if "PGPASSWORD" in os.environ else "postgres"
    pguser = os.environ["PGUSER"] if "PGUSER" in os.environ else "postgres"

    engine = sa.create_engine(f"postgresql://{pguser}:{pgpassword}@{database}:5432/trueprice",
    #connect_args={'options': '-csearch_path=trueprice'}
    )

    check_query = f"select exists(select 1 from trueprice.nyiso_forwardcurve where curveStart='{m.curveStart}' and strip='{m.strip}')"
    r = pd.read_sql(check_query, engine)

    if r is False:
        print("found it")
    else:
        print("not found")

    #r = df.to_sql('data', con = engine, if_exists = 'replace', chunksize=1000, schema="trueprice")

    #if r is None:
    #    print("failed to insert")
    #    return

    #r = pd.read_sql(sa.text("SELECT * FROM trueprice.data"), engine)
    #print(r)

    None

def validate_api(m):
    None

class TLE_Meta:
    def __init__(self, fileName, curveType, controlArea, strip, curveTimestamp):
        self.fileName = fileName
        self.curveType = curveType
        self.controlArea = controlArea
        self.strip = strip
        self.curveStart = curveTimestamp
    
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

if __name__ == "__main__":
    print("Starting")

    files = [
        "./buildContext/data/ForwardCurve_NYISO_2X16_20221209.csv", # strip 1 assuming no HHMMSS is 000000 (midnight)
        "./buildContext/data/ForwardCurve_NYISO_5X16_20221209.csv", # strip 2
        "./buildContext/data/ForwardCurve_NYISO_7X8_20221209.csv", # strip 3
        "./buildContext/data/ForwardCurve_NYISO_7X8_20221209_121212.csv", # strip 3 interday HHMMSS
        "./buildContext/data/ForwardCurve_NYISO_7X8_20221209_cob.csv", # strip 3 cob
        "./buildContext/data/ForwardCurve_NYISO_7X8_20221209_121212.csv", # strip 3 interday (should not do it)
    ]

    # v == validate files names/shape
    # s == store in AWS s3
    # i == ingest into postgres
    # va == validate the data can be retrieved via API
    result = process(files, {"v":validate, "s":storage, "i":ingestion, "va": validate_api})
    if result is not None:
        print("Ingestion Failed")
    else:
        print("Ingestion Succeeded")

    print("Finished Ingestion")
else:
    print("Not a module {}", __name__)