"""
Implements the Slowly Changed Dimensions to insert the data into database
"""
import datetime
import pandas as pd
from ..database_conection import ConnectDatabase

class Nyiso_Energy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the constructors
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def ingestion(self, data):
        """
        Handling Ingestion for nyiso energy
        """

        # WARNING the provided CSV has many empty rows which are not skipped because they are empty strings
        date_cols = ['Zone']
        df = pd.read_csv(data.fileName, header=[2], skiprows=(3,3), dtype={
            'Zone': str, # Bad CSV header (should be curveStart or Month)
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
    
        df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
        df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column


        # using exists always return true or false versus empty/None
        sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
        now = data.curveStart
        eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        

        check_query = f"""
            -- if nothing found, new data, insert it, or do one of these
        
            select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart='{now}'and strip='{data.strip}') -- ignore, db == file based on timestamp
            UNION ALL
            select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<'{now}' and strip='{data.strip}') -- update, db is older
            UNION ALL
            select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart>'{now}' and curvestart<'{eod}' and strip='{data.strip}') -- ignore, db is newer
        """
        r = pd.read_sql(check_query, self.engine)
        same, old_exists, new_exists = r.exists[0], r.exists[1], r.exists[2]

        if same: # if data already exists neglect it
            return "Data already exists based on timestamp and strip"
        
        elif not same and not new_exists and not old_exists: # if data is new then insert it
            r = df.to_sql(f"{data.controlArea}_energy", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
            if r is None:
                if r is None:
                    return "Failed to insert" 
                
        elif old_exists: # if there exists old data, handle it with slowly changing dimensions
            tmp_table_name = f"{data.controlArea}_energy_{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
            r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
            if r is None:
                return "Unable to create data"

            # history/update
            with self.engine.connect() as con:
                curveend = data.curveStart # the new data ends the old data
                backup_query = ''''''
                backup_query = f'''
                    with current as (
                        -- get the current rows in the database, all of them, not just things that will change
                        select id, strip, curvestart, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<='{eod}' and strip='{data.strip}'
                    ),
                    backup as (
                        -- take current rows and insert into database but with a new "curveend" timestamp
                        insert into trueprice.{data.controlArea}_energy_history (id, strip, curvestart, curveend, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount)
                        select id, strip, curvestart, '{curveend}' as curveend, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount
                        from current
                    ),
                    single as (
                        select curvestart from current limit 1
                    )
                    -- update the existing "current" with the new "csv"
                    update trueprice.{data.controlArea}_energy set
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
                        trueprice.{data.controlArea}_energy.strip = newdata.strip 
                        and trueprice.{data.controlArea}_energy.month = newdata.month 
                        and trueprice.{data.controlArea}_energy.curvestart=(select curvestart from single)
                '''
                
                
                # finally execute the query
                r = con.execute(backup_query)            
                con.execute(f"drop table trueprice.{tmp_table_name}")

        elif new_exists:
            return "Newer data in database, abort"
        else:
            return "Ingestion logic error, we should not be here"