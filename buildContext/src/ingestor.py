import pandas as pd
import re
import sqlalchemy as sa
import os
import datetime

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
            timeComponent = "235959" # 24h clock, convert to last possible second so we can sort properly
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


ca = {
    "nyiso": {
        "table": "trueprice.nyiso_forwardcurve",
        "zones": []
    },
    "miso": {
        "table": "trueprice.miso_forwardcurve",
        "zones": []
    },
    "pjm": {
        "table": "trueprice.pjm_forwardcurve",
        "zones": []
    },
    "isone": {
        "table": "trueprice.isone_forwardcurve",
        "zones": []
    },
    "ercot": {
        "table": "trueprice.ercot_forwardcurve",
        "zones": ["north_amount","houston_amount","south_amount","west_amount"],
    }
}

def ingestion(m):
    # WARNING the provided CSV has many empty rows which are not skipped because they are empty strings
    date_cols = ['Zone']
    df = pd.read_csv(m.fileName, header=[2], skiprows=(3,3), dtype={
        'Zone': str, # Bad CSV header (should be curveStart or Month)
        # 'Zone A': pd.Float64Dtype, # ask guys on precision https://beepscore.com/website/2018/10/12/using-pandas-with-python-decimal.html
# ...
        # 'Zone K': pd.Float64Dtype
    }, parse_dates=date_cols).dropna() # acts as context manager
    df[df.columns[1:]] = df[df.columns[1:]].replace('[\$,]', '', regex=True).astype(float) # see warning on Float64Dtype, this removes money and converts to float

    if m.controlArea == "nyiso":
        df.rename(inplace=True, columns={
            'Zone': 'month',
            'ZONE A': 'zone_a_amount',
            'ZONE B': 'zone_b_amount',
            'ZONE C': 'zone_c_amount',
            'ZONE D': 'zone_d_amount',
            'ZONE E': 'zone_e_amount',
            'ZONE F': 'zone_f_amount',
            'ZONE G': 'zone_g_amount',
            'ZONE H': 'zone_h_amount',
            'ZONE I': 'zone_i_amount',
            'ZONE J': 'zone_j_amount',
            'ZONE K': 'zone_k_amount'
            })
    elif m.controlArea == "miso":
        df.rename(inplace=True, columns={
            'Zone': 'month',
            'AMILCIPS': 'amilcips_amount',
            'AMILCILCO': 'amilcilco_amount',
            'AMILIP': 'amilip_amount',
            'INDY HUB': 'indy_amount'
        })
    else:
        return # error

    df.insert(0, 'strip', m.strip) # stored as object, don't freak on dtypes
    df.insert(0, 'curvestart', m.curveStart) # date on file, not the internal zone/month column
    
    print(df)
    print(len(df.index))
    print(df.dtypes)    

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

    # using exists always return true or false versus empty/None
    sod = m.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
    now = m.curveStart
    eod = (m.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    # if no current data, accept new data (even yesterday/backfill or tomorrow/cob)
    # if current data is newer (i.e. curvedate) than new data (i.e. fileanme), ignore it
    # else scd-2
    #check_query = f"select exists(select 1 from trueprice.nyiso_forwardcurve where curvestart>='{m.curveStart}' and curvestart<'{tomorrow}' and strip='{m.strip}')"
    # first is sod to now (in/ex) -- if eq then we just ignore it
    # second is now to eod (ex/ex)

    check_query = f"""
-- if nothing found, new data, insert it, or do one of these
select exists(select 1 from trueprice.{m.controlArea}_forwardcurve where curvestart='{now}'and strip='{m.strip}') -- ignore, db == file based on timestamp
UNION ALL
select exists(select 1 from trueprice.{m.controlArea}_forwardcurve where curvestart>='{sod}' and curvestart<'{now}' and strip='{m.strip}') -- update, db is older
UNION ALL
select exists(select 1 from trueprice.{m.controlArea}_forwardcurve where curvestart>'{now}' and curvestart<'{eod}' and strip='{m.strip}') -- ignore, db is newer
"""
    r = pd.read_sql(check_query, engine)
    same, old_exists, new_exists = r.exists[0], r.exists[1], r.exists[2]

    if same:
        print("Data already exists based on timestamp and strip")
        return
    elif not same and not new_exists and not old_exists:
        r = df.to_sql(f"{m.controlArea}_forwardcurve", con = engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
        if r is None:
            print("Failed to insert")
            return # add error
    elif old_exists:
        # data exists that is older than us for this day
        # # check if data is same versus just existing
        # check_query_2 = f"select exists(select 1 from trueprice.nyiso_forwardcurve where curvestart='{startOfCurveStart}' and curvestart>='{m.curveStart}' and strip='{m.strip}')"        
        # r = pd.read_sql(check_query_2, engine)
        # if r.exists[0]: # same or newer data, so throw error (someone is doing something funky i.e. existing file with new data not just updated data)            
        #     return ExistingDataError(f"Error {m.fileName} already exists in database")

        tmp_table_name = f"nyiso_forwardcurve_{m.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
        r = df.to_sql(f'{tmp_table_name}', con = engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
        if r is None:
            return SQLError(f"failed to create {tmp_table_name}")
        # r = con.execute(f"select * from trueprice.{tmp_table_name}")
        # for l in r:
        #     print(l)

        # history/update
        with engine.connect() as con:
            startOfCurveStart = m.curveStart.strftime('%Y-%m-%d')
            curveend = m.curveStart # the new data ends the old data
            backup_query = f'''
with current as (
    -- get the current rows in the database, all of them, not just things that will change
    select id, strip, curvestart, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount from trueprice.nyiso_forwardcurve where curvestart>='{sod}' and curvestart<='{eod}' and strip='{m.strip}'
),
backup as (
    -- take current rows and insert into database but with a new "curveend" timestamp
    insert into trueprice.nyiso_forwardcurve_history (id, strip, curvestart, curveend, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount)
    select id, strip, curvestart, '{curveend}' as curveend, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount
    from current
),
single as (
    select curvestart from current limit 1
)
-- update the existing "current" with the new "csv"
update trueprice.nyiso_forwardcurve set
curvestart = newdata.curveStart, -- this reflects the intra update, should only be the time not the date
zone_a_amount = newdata.zone_a_amount, -- mindless update all cols, we don't know which ones updated so try them all
zone_b_amount = newdata.zone_b_amount,
zone_c_amount = newdata.zone_c_amount,
zone_d_amount = newdata.zone_d_amount,
zone_e_amount = newdata.zone_e_amount,
zone_f_amount = newdata.zone_f_amount,
zone_g_amount = newdata.zone_g_amount,
zone_h_amount = newdata.zone_h_amount,
zone_i_amount = newdata.zone_i_amount,
zone_j_amount = newdata.zone_j_amount,
zone_k_amount = newdata.zone_k_amount
from 
    trueprice.{tmp_table_name} as newdata -- our csv data
where 
    trueprice.nyiso_forwardcurve.strip = newdata.strip 
    and trueprice.nyiso_forwardcurve.month = newdata.month 
    and trueprice.nyiso_forwardcurve.curvestart=(select curvestart from single)
'''
            print(backup_query)
            r = con.execute(backup_query)            
            #r = pd.read_sql(sa.text("SELECT * FROM trueprice.nyiso_forwardcurve"), engine)
            print(r)
            con.execute(f"drop table trueprice.{tmp_table_name}")
    elif new_exists:
        print("Newer data in database, abort")
        return # needs error
    else:
        print("Ingestion logic error, we should not be here")
        return # needs error

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
        "./buildContext/data/ForwardCurve_MISO_5X16_20230109_084700.csv", # refactoring for MISO from NYISO only
    ]

    # v == validate files names/shape
    # s == store in AWS s3
    # i == ingest into postgres
    # va == validate the data can be retrieved via API
    result = process(files, {"v":validate, "s":storage, "i":ingestion, "va": validate_api})
    if result is not None:
        print(f"Ingestion Failed: {result}")
    else:
        print("Ingestion Succeeded")

    print("Finished Ingestion")
else:
    print("Not a module {}", __name__)