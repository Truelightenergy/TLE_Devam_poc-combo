"""
Implements the Slowly Changed Dimensions to insert the data into database
"""
import datetime
import pandas as pd
from ..database_conection import ConnectDatabase

class Ercot_Energy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def ingestion(self, data):
        """
        Handling Ingestion for energy for iso ercot
        """

        # WARNING the provided CSV has many empty rows which are not skipped because they are empty strings
        date_cols = ['Zone']
        df = pd.read_csv(data.fileName, header=[2], skiprows=(3,3), dtype={
            'Zone': str, # Bad CSV header (should be curveStart or Month)
        }, parse_dates=date_cols) # acts as context manager
        df.dropna(axis=1, how='all', inplace=True)
        df.rename(columns={df.columns[1]: 'Strip'}, inplace=True)

        df[df.columns[2:]] = df[df.columns[2:]].replace('[\$,]', '', regex=True).astype(float) # see warning on Float64Dtype, this removes money and converts to float

        df.rename(inplace=True, columns={
            'Zone': 'month', 
            'Strip': 'strip', 
            'NORTH ZONE':'north_amount',
            'HOUSTON ZONE':'houston_amount',
            'SOUTH ZONE':'south_amount',
            'WEST ZONE':'west_amount'
        })
    
        # df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
        df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column


        # using exists always return true or false versus empty/None
        sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
        now = data.curveStart
        eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        

        check_query = f"""
            -- if nothing found, new data, insert it, or do one of these
        
            select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart='{now}') -- ignore, db == file based on timestamp
            UNION ALL
            select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<'{now}' ) -- update, db is older
            UNION ALL
            select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart>'{now}' and curvestart<'{eod}' ) -- ignore, db is newer
        """
        r = pd.read_sql(check_query, self.engine)
        same, old_exists, new_exists = r.exists[0], r.exists[1], r.exists[2]

        if same: # if data already exists neglect it
            return "Data already exists based on timestamp and strip"
        
        elif not same and not new_exists and not old_exists: # if data is new then insert it
            r = df.to_sql(f"{data.controlArea}_energy", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
            if r is not None:
                return "Data Inserted"
            return "Failed to insert" 
                
        elif old_exists: # if there exists old data, handle it with slowly changing dimensions
            tmp_table_name = f"{data.controlArea}_energy_{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
            r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
            if r is None:
                return "Unable to create data"

            # history/update
            with self.engine.connect() as con:
                curveend = data.curveStart # the new data ends the old data
                backup_query = f'''
                    with current as (
                        -- get the current rows in the database, all of them, not just things that will change
                        select id, strip, curvestart, month, north_amount, houston_amount, south_amount, west_amount from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<='{eod}'
                    ),
                    backup as (
                        -- take current rows and insert into database but with a new "curveend" timestamp
                        insert into trueprice.{data.controlArea}_energy_history (id, strip, curvestart, curveend, month, north_amount, houston_amount, south_amount, west_amount)
                        select id, strip, curvestart, '{curveend}' as curveend, month, north_amount, houston_amount, south_amount, west_amount
                        from current
                    ),
                    single as (
                        select curvestart from current limit 1
                    )
                    -- update the existing "current" with the new "csv"
                    --north_amount, houston_amount, south_amount, west_amount
                    update trueprice.{data.controlArea}_energy set
                    month = newdata.month,
                    curvestart = newdata.curveStart, -- this reflects the intra update, should only be the time not the date
                    north_amount = newdata.north_amount, -- mindless update all cols, we don't know which ones updated so try them all
                    houston_amount = newdata.houston_amount,
                    south_amount = newdata.south_amount,
                    west_amount = newdata.west_amount
                    from 
                        trueprice.{tmp_table_name} as newdata -- our csv data
                    where 
                        trueprice.{data.controlArea}_energy.strip = newdata.strip 
                        and trueprice.{data.controlArea}_energy.month = newdata.month 
                        and trueprice.{data.controlArea}_energy.curvestart=(select curvestart from single)
                '''                
            
                
                
                
                # finally execute the query
                r = con.execute(backup_query)            
                con.execute(f"drop table trueprice.{tmp_table_name}")
            return "Data Inserted"

        elif new_exists:
            return "Newer data in database, abort"
        else:
            return "Ingestion logic error, we should not be here"