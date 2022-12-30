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
        'Zone': str, # Bad CSV header (should be curveStart or Month)
        # 'Zone A': pd.Float64Dtype, # ask guys on precision https://beepscore.com/website/2018/10/12/using-pandas-with-python-decimal.html
# ...
        # 'Zone K': pd.Float64Dtype
    }, parse_dates=date_cols).dropna() # acts as context manager
    df[df.columns[1:]] = df[df.columns[1:]].replace('[\$,]', '', regex=True).astype(float) # see warning on Float64Dtype, this removes money and converts to float

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

    df.insert(0, 'strip', m.strip) # stored as object, don't freak on dtypes
    df.insert(0, 'curvestart', m.curveStart) # date on file, not the internal zone/month column
    
    print(df)
    print(len(df.index))
    print(df.dtypes)

    """
    \c trueprice
    CREATE DATABASE trueprice;

        create table nyiso_forwardcurve ( -- history table differs
        id serial PRIMARY KEY,
        strip varchar(4), -- 7X8, 2X16, 7X24, etc. maybe enum one day
        curvestart TIMESTAMPTZ, -- per file name (sans tz)
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
        curvestart TIMESTAMPTZ, -- per original file name
        curveend TIMESTAMPTZ, -- per new file name
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

    # using exists always return true or false versus empty/None
    startOfCurveStart = m.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
    check_query = f"select exists(select 1 from trueprice.nyiso_forwardcurve where curvestart='{startOfCurveStart}' and strip='{m.strip}')"
    r = pd.read_sql(check_query, engine)
    if not r.exists[0]: # new data
        # index/col broken
        r = df.to_sql('nyiso_forwardcurve', con = engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
        if r is None:
            print("failed to insert")
    else:
        # check if data is same versus just existing
        check_query_2 = f"select exists(select 1 from trueprice.nyiso_forwardcurve where curvestart='{startOfCurveStart}' and curvestart>='{m.curveStart}' and strip='{m.strip}')"        
        r = pd.read_sql(check_query_2, engine)
        if r.exists[0]: # same or newer data, so throw error (someone is doing something funky)            
            return ExistingDataError(f"Error {m.fileName} already exists in database")

        tmp_table_name = f"nyiso_forwardcurve_{m.snake_timestamp()}"

        r = df.to_sql(f'{tmp_table_name}', con = engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
        if r is None:
            return SQLError(f"failed to create {tmp_table_name}")
        # r = con.execute(f"select * from trueprice.{tmp_table_name}")
        # for l in r:
        #     print(l)

        with engine.connect() as con:
            curveend = m.curveStart # file f is update to file f-1 where f is same date but f is updated time
            backup_query = f'''
with current as (
    select id, strip, curvestart, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount from trueprice.nyiso_forwardcurve where curvestart='{startOfCurveStart}' and strip='{m.strip}'
),
backup as (
    insert into trueprice.nyiso_forwardcurve_history (id, strip, curvestart, curveend, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount)
    select id, strip, curvestart, '{curveend}' as curveend, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount
    from current
)
update trueprice.nyiso_forwardcurve set
curvestart = newdata.curveStart,
zone_a_amount = newdata.zone_a_amount,
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
from trueprice.{tmp_table_name} as newdata
where trueprice.nyiso_forwardcurve.strip = newdata.strip and trueprice.nyiso_forwardcurve.month = newdata.month and trueprice.nyiso_forwardcurve.curvestart='{startOfCurveStart}'
'''
            print(backup_query)
            r = con.execute(backup_query)            
            #r = pd.read_sql(sa.text("SELECT * FROM trueprice.nyiso_forwardcurve"), engine)
            print(r)
            con.execute(f"drop table trueprice.{tmp_table_name}")
            

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
#        "./buildContext/data/ForwardCurve_NYISO_7X8_20221209.csv", # strip 3
        "./buildContext/data/ForwardCurve_NYISO_7X8_20221209_121212.csv", # strip 3 interday HHMMSS
        #"./buildContext/data/ForwardCurve_NYISO_7X8_20221209_cob.csv", # strip 3 cob
        #"./buildContext/data/ForwardCurve_NYISO_7X8_20221209_121212.csv", # strip 3 interday (should not do it)
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