

# STATUS
# need to know which columns make the row unique so we can do the update, we can't use month/strip here because they don't change

"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
import datetime
from utils.database_connection import ConnectDatabase
from .helpers.nyiso_energy_helper import NyisoEnergyHelper

class Nyiso_energy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the connection to the databases
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()
        self.herlper = NyisoEnergyHelper()

    #Zone ID,Ancillary,Load Zone,Month,Price,Billing Determinant,,,,

    def ingestion(self, data):


        try:
            df = pd.read_csv(data.fileName, header=None)
            df= self.herlper.setup_dataframe(df)
            if not isinstance(df, pd.DataFrame):
               return "File Format Not Matched"
            

            df['date'] = pd.to_datetime(df['date'])
            df['data'] = df['data'].astype(float)
            df.rename(inplace=True, columns={
                'block_type' : 'strip', 
                'date' : 'month'
            })

            if "_cob" in data.fileName.lower():
                df.insert(0, 'cob', 1)
            else:
                df.insert(0, 'cob', 0)

            df["cob"] = df["cob"].astype(bool)

            df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column
            # df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
            


            # using exists always return true or false versus empty/None
            sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
            now = data.curveStart
            eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

            check_query = f"""
                -- if nothing found, new data, insert it, or do one of these
            
                select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart='{now}') -- ignore, "db == file" based on timestamp
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<='{now}') -- update, db already exists
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_energy where curvestart>='{now}' and curvestart<'{eod}' ) -- ignore, db is equal or newer
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
                return "Insert aborted, failed to insert new data"
                    
            elif old_exists: # perform scd-2
                tmp_table_name = f"{data.controlArea}_energy_{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
                r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
                if r is None:
                    return "Unable to create temp data table for update"
            

                with self.engine.connect() as con:
                    curveend = data.curveStart # the new data ends the old data
                    backup_query = f'''

                    
                        -- insertion to the database in history table
                            with current as (
                                -- get the current rows in the database, all of them, not just things that will change

                                select id, cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                                from trueprice.{data.controlArea}_energy where curvestart>='{sod}' and curvestart<='{eod}'
                            ),
                            backup as (
                                -- take current rows and insert into database but with a new "curveend" timestamp

                                insert into trueprice.{data.controlArea}_energy_history ( cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

                                select  cob, month, curvestart, '{curveend}' as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
                                from current
                            ),
                            single as (
                                select curvestart from current limit 1
                            ),
                        
                        
                        -- update the existing "current" with the new "csv"
                        
                            deletion as(
                            DELETE from trueprice.{data.controlArea}_energy
                            WHERE curvestart = (select curvestart from single)

                            ),

                            updation as (
                            insert into trueprice.{data.controlArea}_energy ( cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

                            select  cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
                                from trueprice.{tmp_table_name}
                            )
                        select * from trueprice.{data.controlArea}_energy;
                   
                    
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
            return "Failure in Ingestion"
