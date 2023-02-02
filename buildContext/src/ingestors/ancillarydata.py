import pandas as pd
import re
import sqlalchemy as sa
import os
import datetime

# ancillarydata
def ingestion(m):
    df = pd.read_csv(m.fileName, parse_dates=['Month'])
    df.rename(inplace=True, columns={
        'Zone ID': 'zone_id',
        'Load Zone': 'load_zone',
        'Month': 'month',
        'RTLO ($/MWh)': 'rtlo_mwh',
        'DALO ($/MWh)': 'dalo_mwh',
        'Deviations ($/MWh)': 'deviations_mwh',
        'NCP ($/MW)': 'ncp_mw'
    })

    df.drop(columns=["zone_id"], inplace=True)

    df.insert(0, 'strip', m.strip) # stored as object, don't freak on dtypes
    df.insert(0, 'curvestart', m.curveStart) # date on file, not the internal zone/month column
    
    print(df)
    print(len(df.index))
    print(df.dtypes)

    database = os.environ["DATABASE"] if "DATABASE" in os.environ else "localhost"
    pgpassword = os.environ["PGPASSWORD"] if "PGPASSWORD" in os.environ else "postgres"
    pguser = os.environ["PGUSER"] if "PGUSER" in os.environ else "postgres"

    engine = sa.create_engine(f"postgresql://{pguser}:{pgpassword}@{database}:5432/trueprice")

    sod = m.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
    now = m.curveStart
    eod = (m.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    check_query = f"""
-- if nothing found, new data, insert it, or do one of these
select exists(select 1 from trueprice.{m.controlArea}_ancillarydata where curvestart='{now}'and strip='{m.strip}') -- ignore, db == file based on timestamp
UNION ALL
select exists(select 1 from trueprice.{m.controlArea}_ancillarydata where curvestart>='{sod}' and curvestart<'{now}' and strip='{m.strip}') -- update, db is older
UNION ALL
select exists(select 1 from trueprice.{m.controlArea}_ancillarydata where curvestart>'{now}' and curvestart<'{eod}' and strip='{m.strip}') -- ignore, db is newer
"""
    r = pd.read_sql(check_query, engine)
    same, old_exists, new_exists = r.exists[0], r.exists[1], r.exists[2]

    if same:
        print("Data already exists based on timestamp and strip")
        return
    elif not same and not new_exists and not old_exists:
        r = df.to_sql(f"{m.controlArea}_ancillarydata", con = engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
        if r is None:
            print("Failed to insert")
            return # add error
    elif old_exists:
        tmp_table_name = f"{m.controlArea}_ancillarydata_{m.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
        r = df.to_sql(f'{tmp_table_name}', con = engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
        if r is None:
            return SQLError(f"failed to create {tmp_table_name}")

        with engine.connect() as con:
            startOfCurveStart = m.curveStart.strftime('%Y-%m-%d')
            curveend = m.curveStart # the new data ends the old data
            backup_query = ''''''
            if m.controlArea == "isone":
                backup_query = f'''
with current as (
    -- get the current rows in the database, all of them, not just things that will change
    select id, strip, curvestart, load_zone, rtlo_mwh, dalo_mwh, deviations_mwh, ncp_mw from trueprice.{m.controlArea}_ancillarydata where curvestart>='{sod}' and curvestart<='{eod}' and strip='{m.strip}'
),
backup as (
    -- take current rows and insert into database but with a new "curveend" timestamp
    insert into trueprice.{m.controlArea}_ancillarydata_history (id, strip, curvestart, curveend, load_zone, rtlo_mwh, dalo_mwh, deviations_mwh, ncp_mw)
    select id, strip, curvestart, '{curveend}' as curveend, load_zone, rtlo_mwh, dalo_mwh, deviations_mwh, ncp_mw
    from current
),
single as (
    select curvestart from current limit 1
)
-- update the existing "current" with the new "csv"
update trueprice.{m.controlArea}_ancillarydata set
curvestart = newdata.curveStart, -- this reflects the intra update, should only be the time not the date
load_zone = newdata.load_zone, -- mindless update all cols, we don't know which ones updated so try them all
rtlo_mwh = newdata.rtlo_mwh,
dalo_mwh = newdata.dalo_mwh,
deviations_mwh = newdata.deviations_mwh,
ncp_mw = newdata.ncp_mw
from 
    trueprice.{tmp_table_name} as newdata -- our csv data
where 
    trueprice.{m.controlArea}_ancillarydata.strip = newdata.strip 
    and trueprice.{m.controlArea}_ancillarydata.month = newdata.month 
    and trueprice.{m.controlArea}_ancillarydata.curvestart=(select curvestart from single)
'''        
            #elif m.controlArea == "nyiso":
            # etc.
            else:
                print("Unknown update,abort")
                return
            print(backup_query)
            r = con.execute(backup_query)            
            print(r)
            con.execute(f"drop table trueprice.{tmp_table_name}")
    elif new_exists:
        print("Newer data in database, abort")
        return # needs error
    else:
        print("Ingestion logic error, we should not be here")
        return # needs error

    return