import pandas as pd
import re
import sqlalchemy as sa
import os

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
    df = pd.read_csv(f, header=[2], skiprows=(3,3), dtype={
        'Zone': str, # Month aka Zone due to bad header
        # 'Zone A': pd.Float64Dtype, # ask guys on precision https://beepscore.com/website/2018/10/12/using-pandas-with-python-decimal.html
        # 'Zone B': pd.Float64Dtype,
        # 'Zone C': pd.Float64Dtype,
        # 'Zone D': pd.Float64Dtype,
        # 'Zone E': pd.Float64Dtype,
        # 'Zone F': pd.Float64Dtype,
        # 'Zone G': pd.Float64Dtype,
        # 'Zone H': pd.Float64Dtype,
        # 'Zone I': pd.Float64Dtype,
        # 'Zone J': pd.Float64Dtype,
        # 'Zone K': pd.Float64Dtype
    }, parse_dates=date_cols).dropna() # acts as context manager
    df[df.columns[1:]] = df[df.columns[1:]].replace('[\$,]', '', regex=True).astype(float) # see warning on Float64Dtype, this removes money and converts to float
#    print(df)
#    print(len(df.index))
#    print(df.dtypes)

    #create table test_data ( -- history table differs
    # id serial PRIMARY KEY, 
    # zone_a_amount numeric(12,8), 
    # zone_b_amount numeric(12,8),
    # zone_c_amount numeric(12,8),
    # zone_d_amount numeric(12,8), 
    # zone_e_amount numeric(12,8),     
    # zone_f_amount numeric(12,8), 
    # zone_g_amount numeric(12,8),
    # zone_h_amount numeric(12,8),
    # zone_i_amount numeric(12,8), 
    # zone_j_amount numeric(12,8),     
    # zone_k_amount numeric(12,8),    
    # curveStart TIMESTAMP
    # );

    database = os.environ["DATABASE"]
    pgpassword = os.environ["PGPASSWORD"]
    pguser = os.environ["PGUSER"]
    engine = sa.create_engine(f"postgresql://{pguser}:{pgpassword}@{database}:5432/trueprice",
    #connect_args={'options': '-csearch_path=trueprice'}
    )

    r = df.to_sql('data', con = engine, if_exists = 'replace', chunksize=1000, schema="trueprice")

    if r is None:
        print("failed to insert")
        return

    r = pd.read_sql(sa.text("SELECT * FROM trueprice.data"), engine)
    print(r)

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
        "./buildContext/data/ForwardCurve_NYISO_2X16_20221209.csv",
        "./buildContext/data/ForwardCurve_NYISO_5X16_20221209.csv",
        "./buildContext/data/ForwardCurve_NYISO_7X8_20221209.csv"
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