"""
Implements the Slowly Changed Dimensions to insert the data into database
"""
import datetime
import pandas as pd
from database_connection import ConnectDatabase

class Pjm_Energy:
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
        Handling Ingestion for pjm energies
        """
        try:

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
                'AECO':'aeco_amount',
                'AEP':'aep_amount',
                'APS':'aps_amount', 
                'ATSI':'atsi_amount', 
                'BGE':'bge_amount', 
                'COMED':'comed_amount', 
                'DAY':'day_amount', 
                'DEOK':'deok_amount', 
                'DOM':'dom_amount', 
                'DPL':'dpl_amount', 
                'DUQ':'duq_amount', 
                'JCPL':'jcpl_amount', 
                'METED':'meted_amount', 
                'PECO':'peco_amount', 
                'PENELEC':'penelec_amount', 
                'PEPCO':'pepco_amount', 
                'PPL':'ppl_amount', 
                'PSEG':'pseg_amount', 
                'RECO':'reco_amount', 
                'WEST HUB':'west_amount', 
                'AD HUB':'ad_amount', 
                'NI HUB':'ni_amount', 
                'EAST HUB':'east_amount'
            })
        
            if "_cob" in data.fileName:
                df.insert(0, 'cob', 1)
            else:
                df.insert(0, 'cob', 0)

            df["cob"] = df["cob"].astype(bool)
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
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<'{eod}' and cob ) -- ignore, db has cob already
            """
            r = pd.read_sql(check_query, self.engine)
            same, old_exists, new_exists, cob_exists = r.exists[0], r.exists[1], r.exists[2], r.exists[3]

            if same: # if data already exists neglect it
                return "Insert aborted, data already exists based on timestamp and strip"
            
            elif cob_exists:
                return "Insert aborted, existing data marked with cob"
            
            elif new_exists:
                return "Insert aborted, newer data in database"            
            
            elif not same and not new_exists and not old_exists and not cob_exists: # upsert new data
                r = df.to_sql(f"{data.controlArea}_energy", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
                if r is not None:
                    return "Data Inserted"
                return "Failed to insert" 
                    
            elif old_exists: # perform scd-2
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
                            select id, strip, cob, curvestart, month, aeco_amount, aep_amount, aps_amount, atsi_amount, bge_amount, comed_amount, day_amount, deok_amount, dom_amount, dpl_amount, duq_amount, jcpl_amount, meted_amount, peco_amount, penelec_amount, pepco_amount, ppl_amount, pseg_amount, reco_amount, west_amount, ad_amount, ni_amount, east_amount from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<='{eod}' 
                        ),
                        backup as (
                            -- take current rows and insert into database but with a new "curveend" timestamp
                            insert into trueprice.{data.controlArea}_energy_history (id, strip, cob, curvestart, curveend, month, aeco_amount, aep_amount, aps_amount, atsi_amount, bge_amount, comed_amount, day_amount, deok_amount, dom_amount, dpl_amount, duq_amount, jcpl_amount, meted_amount, peco_amount, penelec_amount, pepco_amount, ppl_amount, pseg_amount, reco_amount, west_amount, ad_amount, ni_amount, east_amount)
                            select id, strip, cob,  curvestart, '{curveend}' as curveend, month, aeco_amount, aep_amount, aps_amount, atsi_amount, bge_amount, comed_amount, day_amount, deok_amount, dom_amount, dpl_amount, duq_amount, jcpl_amount, meted_amount, peco_amount, penelec_amount, pepco_amount, ppl_amount, pseg_amount, reco_amount, west_amount, ad_amount, ni_amount, east_amount
                            from current
                        ),
                        single as (
                            select curvestart from current limit 1
                        )
                        -- update the existing "current" with the new "csv"
                        update trueprice.{data.controlArea}_energy set
                        strip = newdata.strip,
                        month = newdata.month,
                        cob = newdata.cob,
                        curvestart = newdata.curveStart, -- this reflects the intra update, should only be the time not the date
                        aeco_amount = newdata.aeco_amount,
                        aep_amount = newdata.aep_amount,
                        aps_amount = newdata.aps_amount,
                        atsi_amount = newdata.atsi_amount,
                        bge_amount = newdata.bge_amount,
                        comed_amount = newdata.comed_amount,
                        day_amount = newdata.day_amount,
                        deok_amount = newdata.deok_amount,
                        dom_amount = newdata.dom_amount,
                        dpl_amount = newdata.dpl_amount,
                        duq_amount = newdata.duq_amount,
                        jcpl_amount = newdata.jcpl_amount,
                        meted_amount = newdata.meted_amount,
                        peco_amount = newdata.peco_amount,
                        penelec_amount = newdata.penelec_amount,
                        pepco_amount = newdata.pepco_amount,
                        ppl_amount = newdata.ppl_amount,
                        pseg_amount = newdata.pseg_amount,
                        reco_amount = newdata.reco_amount,
                        west_amount = newdata.west_amount,
                        ad_amount = newdata.ad_amount,
                        ni_amount = newdata.ni_amount,
                        east_amount = newdata.east_amount
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
                return "Data updated"

            else:
                return "Unknown insert/update error"
        except:
            import traceback, sys
            print(traceback.format_exc())
            return traceback.format_exc()