

# STATUS
# need to know which columns make the row unique so we can do the update, we can't use month/strip here because they don't change

"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
import datetime
from utils.database_connection import ConnectDatabase
from .helpers.miso_nonenergy_helpler import MisoNonEnergyHelper

class Miso_NonEnergy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the connection to the databases
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()
        self.herlper = MisoNonEnergyHelper()

    #Zone ID,Ancillary,Load Zone,Month,Price,Billing Determinant,,,,

    def ingestion(self, data):


        try:
            df = pd.read_csv(data.fileName, header=None)
            df= self.herlper.setup_dataframe(df)
            if not isinstance(df, pd.DataFrame):
               return "File Format Not Matched"
            
            df['date'] = pd.to_datetime(df['date'])
            df['data'] = df['data'].astype(float)
            # df = df.fillna(0.0)
            

            df.rename(inplace=True, columns={
                'block_type' : 'strip', 
                'date' : 'month'
            })

            df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column
            # df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
            
            

            # using exists always return true or false versus empty/None
            sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
            now = data.curveStart
            eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

            check_query = f"""
                -- if nothing found, new data, insert it, or do one of these
                
                select exists(select 1 from trueprice.{data.controlArea}_nonenergy where curvestart='{now}') -- ignore, db == file based on timestamp
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_nonenergy where curvestart>='{sod}' and curvestart<'{now}') -- update, db is older
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_nonenergy where curvestart>'{now}' and curvestart<'{eod}') -- ignore, db is newer
            """
            query_result = pd.read_sql(check_query, self.engine)
            same, old_exists, new_exists = query_result.exists[0], query_result.exists[1], query_result.exists[2]

            if same: # if data already exists neglect it
                return "Data already exists based on timestamp and strip"
            
            elif not same and not new_exists and not old_exists: # if data is new then insert it
                r = df.to_sql(f"{data.controlArea}_nonenergy", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
                if r is not None:
                    return "Data Inserted"
                return "Failed to insert"         

            elif old_exists: # if there exists old data, handle it with slowly changing dimensions
                tmp_table_name = f"{data.controlArea}_nonenergy{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
                r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
                if r is None:
                    return "Unable to create data"

                with self.engine.connect() as con:
                    curveend = data.curveStart # the new data ends the old data
                    backup_query = f'''

                    
                        -- insertion to the database in history table
                            with current as (
                                -- get the current rows in the database, all of them, not just things that will change

                                select id, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                                from trueprice.{data.controlArea}_nonenergy where curvestart>='{sod}' and curvestart<='{eod}'
                            ),
                            backup as (
                                -- take current rows and insert into database but with a new "curveend" timestamp

                                insert into trueprice.{data.controlArea}_nonenergy_history (month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

                                select month, curvestart, '{curveend}' as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
                                from current
                            ),
                            single as (
                                select curvestart from current limit 1
                            ),
                        
                        
                        -- update the existing "current" with the new "csv"
                        
                            deletion as(
                            DELETE from trueprice.{data.controlArea}_nonenergy
                            WHERE curvestart = (select curvestart from single)

                            ),

                            updation as (
                            insert into trueprice.{data.controlArea}_nonenergy (month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

                            select month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
                                from trueprice.{tmp_table_name}
                            )
                        select * from trueprice.{data.controlArea}_nonenergy;
                   
                    
                    '''       
                

                    # finally execute the query
                    r = con.execute(backup_query)            
                    con.execute(f"drop table trueprice.{tmp_table_name}")
                return "Data Inserted"

            elif new_exists:
                return "Newer data in database, abort"
            else:
                return "Ingestion logic error, we should not be here"
        except:
            import traceback, sys
            print(traceback.format_exc())
            return "Unable to make it to db."
