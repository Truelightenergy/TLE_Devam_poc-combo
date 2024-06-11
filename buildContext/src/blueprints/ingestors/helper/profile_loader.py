"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
import datetime
from ..ingestor_model import IngestorUtil
from utils.configs import read_config

config = read_config()

class Profile_Loader:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        self.secret_key = config['secret_key']
        self.secret_salt = config['secret_salt']
        self.db_util = IngestorUtil(self.secret_key, self.secret_salt)
        
    def ingestion(self, df):
        try:
            df= self.setup_dataframe(df)
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
            
                select exists(select 1 from trueprice.curves_data where curvestart='{now}') -- ignore, "db == file" based on timestamp
                UNION ALL
                select exists(select 1 from trueprice.curves_data where curvestart>='{sod}' and curvestart<='{now}') -- update, db already exists
                UNION ALL
                select exists(select 1 from trueprice.curves_data where curvestart>='{now}' and curvestart<'{eod}' ) -- ignore, db is equal or newer
                UNION ALL
                select exists(select 1 from trueprice.curves_data where curvestart>='{sod}' and curvestart<'{eod}' and cob ) -- ignore, db has cob already
            """
            r = pd.read_sql(check_query, self.db_util.engine)
            same, old_exists, new_exists, cob_exists = r.exists[0], r.exists[1], r.exists[2], r.exists[3]
            

            if same: # if data already exists neglect it
                return "Insert aborted, data already exists based on timestamp and strip"
            
            elif cob_exists:
                return "Insert aborted, existing data marked with cob"
            
            elif new_exists:
                return "Insert aborted, newer data in database"

            elif not same and not new_exists and not old_exists and not cob_exists: # upsert new data
                r = df.to_sql(f"curves_data", con = self.db_util.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
                if r is not None:
                    return "Data Inserted"
                return "Insert aborted, failed to insert new data"
                    
            elif old_exists: # perform scd-2
                tmp_table_name = f"curves_data_{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
                r = df.to_sql(f'{tmp_table_name}', con = self.db_util.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
                if r is None:
                    return "Unable to create temp data table for update"
                            

                with self.db_util.engine.connect() as con:
                    curveend = data.curveStart # the new data ends the old data
                    backup_query = f'''

                    
                        -- insertion to the database in history table
                            with current as (
                                -- get the current rows in the database, all of them, not just things that will change

                                select id, cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                                from trueprice.curves_data where curvestart>='{sod}' and curvestart<='{eod}'
                            ),
                            backup as (
                                -- take current rows and insert into database but with a new "curveend" timestamp

                                insert into trueprice.curves_data_history ( cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

                                select  cob, month, curvestart, '{curveend}' as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
                                from current
                            ),
                            single as (
                                select curvestart from current limit 1
                            ),
                        
                        
                        -- update the existing "current" with the new "csv"
                        
                            deletion as(
                            DELETE from trueprice.curves_data
                            WHERE curvestart = (select curvestart from single)

                            ),

                            updation as (
                            insert into trueprice.curves_data ( cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

                            select  cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
                                from trueprice.{tmp_table_name}
                            )
                        select * from trueprice.curves_data;
                   
                    
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

    def renaming_columns(self, df):
        """
        rename the columns accordingly
        """

        df.columns =  df.iloc[0].astype(str)
        df = df.drop([df.index[0]])
        df.reset_index(inplace=True, drop=True)
        
        df.rename(inplace=True, columns={
                df.columns[0]: 'Date'
            })
    
        return df

    def setup_dataframe(self, data_frame):
        """
        formats the data frame into proper format
        """
        try:
            df = data_frame
            df_data = df.iloc[10:]
            df_data = df_data.dropna(axis = 1, how = 'all')
            df_data = df_data.dropna(axis = 0, how = 'all')
            df_data.reset_index(inplace=True, drop=True)
            df_data = self.renaming_columns(df_data)
            
            
            # making the headers dataframe and tranposing it
            df_info = df.iloc[1:9]
            df_info = df_info.dropna(axis = 1, how = 'all')
            df_info = df_info.dropna(axis = 0, how = 'all')
            df_info.reset_index(inplace=True, drop=True)
            df_info = df_info.transpose()
            df_info.columns = df_info.iloc[0]
            df_info = df_info.drop(df_info.index[0])
            df_info.reset_index(inplace=True, drop=True)

            if df_info.isnull().values.any():
                raise Exception("File Format Not Matched")
            

            # formating the dataframe
            dataframes = []
            for index, col in enumerate(df_data.columns[1:]):
                
                
                tmp_df = df_data[["Date"]].copy()
                tmp_df.loc[:, 'Data'] = df_data.iloc[:, index+1]
                labels = ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component"]
                for label in labels:
                    tmp_df[label] = df_info.at[index, label]
                if isinstance(col, float):
                    tmp_df["Sub Cost Component"] = tmp_df["Cost Component"]
                else:
                    tmp_df["Sub Cost Component"] = col
                tmp_df = tmp_df.reset_index(drop=True)
                dataframes.append(tmp_df)

            resultant_df = pd.concat(dataframes, axis=0)
            resultant_df=resultant_df.sort_values("Date")
            resultant_df['Data'].fillna(0, inplace=True)
            resultant_df['Data'].replace('[\$,]', '', regex=True, inplace=True)
            resultant_df['Data'].replace('[\%,]', '', regex=True, inplace=True)
            resultant_df.reset_index(drop=True, inplace=True)

            # column renaming
            resultant_df = resultant_df.rename(columns=lambda x: x.replace(' ', '_').lower())
            return resultant_df
        except Exception as e:

            import traceback, sys
            print(traceback.format_exc())
            return "File Format Not Matched"
    