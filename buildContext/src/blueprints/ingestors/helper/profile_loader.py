"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
import datetime
from ..ingestor_model import IngestorUtil
from utils.configs import read_config
from ...hierarchy_utils.utils import BaseTableHierarchy
import time

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
        self.hierarchy = BaseTableHierarchy()
        
    def ingestion(self, data):
        try:
            df = pd.read_csv(data.fileName, header=None)
            temp_time = time.time()
            df= self.setup_dataframe(df, data.curveType)
            print("time.time()-temp_time total", time.time()-temp_time)
            if not isinstance(df, pd.DataFrame):
               return "File Format Not Matched"
            

            df['date'] = pd.to_datetime(df['date'])
            df['data'] = df['data'].astype(float)
            df.rename(inplace=True, columns={
                'date' : 'month'
            })

            # if "_cob" in data.fileName.lower():
            #     df.insert(0, 'cob', 1)
            # else:
            #     df.insert(0, 'cob', 0)

            # df["cob"] = df["cob"].astype(bool)

            df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column
            # df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
            


            # using exists always return true or false versus empty/None
            # sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
            now = data.curveStart
            # eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

            # check_query = f"""
            #     -- if nothing found, new data, insert it, or do one of these
            
            #     select exists(select 1 from trueprice.curves_data where curvestart='{now}') -- ignore, "db == file" based on timestamp
            #     UNION ALL
            #     select exists(select 1 from trueprice.curves_data where curvestart>='{sod}' and curvestart<='{now}') -- update, db already exists
            #     UNION ALL
            #     select exists(select 1 from trueprice.curves_data where curvestart>='{now}' and curvestart<'{eod}' ) -- ignore, db is equal or newer
            #     UNION ALL
            #     select exists(select 1 from trueprice.curves_data where curvestart>='{sod}' and curvestart<'{eod}' and cob ) -- ignore, db has cob already
            # """
            check_query = f"""
            select exists(select 1 from trueprice.curves_data where curvestart='{now}') -- ignore, "db == file" based on timestamp
            """
            # r = pd.read_sql(check_query, self.db_util.engine)
            # same, old_exists, new_exists, cob_exists = r.exists[0], r.exists[1], r.exists[2], r.exists[3]
            r = pd.read_sql(check_query, self.db_util.engine)
            same = r.exists[0]
            

            if same: # if data already exists neglect it
                return "Insert aborted, data already exists based on timestamp and strip"
            
            # elif cob_exists:
            #     return "Insert aborted, existing data marked with cob"
            
            # elif new_exists:
            #     return "Insert aborted, newer data in database"

            # elif not same and not new_exists and not old_exists and not cob_exists: # upsert new data
            r = df.to_sql(f"curves_data", con = self.db_util.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
            if r is not None:
                return "Data Inserted"
            return "Insert aborted, failed to insert new data"
                    
            # elif old_exists: # perform scd-2
            #     tmp_table_name = f"curves_data_{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
            #     r = df.to_sql(f'{tmp_table_name}', con = self.db_util.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
            #     if r is None:
            #         return "Unable to create temp data table for update"
                            

            #     with self.db_util.engine.connect() as con:
            #         curveend = data.curveStart # the new data ends the old data
            #         backup_query = f'''

                    
            #             -- insertion to the database in history table
            #                 with current as (
            #                     -- get the current rows in the database, all of them, not just things that will change

            #                     select id, cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
            #                     from trueprice.curves_data where curvestart>='{sod}' and curvestart<='{eod}'
            #                 ),
            #                 backup as (
            #                     -- take current rows and insert into database but with a new "curveend" timestamp

            #                     insert into trueprice.curves_data_history ( cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

            #                     select  cob, month, curvestart, '{curveend}' as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
            #                     from current
            #                 ),
            #                 single as (
            #                     select curvestart from current limit 1
            #                 ),
                        
                        
            #             -- update the existing "current" with the new "csv"
                        
            #                 deletion as(
            #                 DELETE from trueprice.curves_data
            #                 WHERE curvestart = (select curvestart from single)

            #                 ),

            #                 updation as (
            #                 insert into trueprice.curves_data ( cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)

            #                 select  cob, month, curvestart, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component
            #                     from trueprice.{tmp_table_name}
            #                 )
            #             select * from trueprice.curves_data;
                   
                    
            #         '''          
                

            #         # finally execute the query
            #         r = con.execute(backup_query)
            #         con.execute(f"drop table trueprice.{tmp_table_name}")
            #     return "Data updated"
            # else:
            #     return "Unknown insert/update error"
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

    def setup_dataframe(self, data_frame, curveType):
        """
        formats the data frame into proper format
        """
        try:
            # data_frame = data_frame.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            data_frame.replace('', pd.NA, inplace=True)
            data_frame.dropna(axis = 1, how = 'all', inplace = True)
            data_frame.dropna(axis = 0, how = 'all', inplace = True)
            header = data_frame.loc[:data_frame.loc[data_frame[0].isin(['Month', 'Date'])].index[0]-1]
            data = data_frame.loc[data_frame.loc[data_frame[0].isin(['Month', 'Date'])].index[0]:]

            # dataprocessing for headers/labels
            header = header.transpose()
            header.dropna(axis = 0, how = 'all', inplace = True)
            # header.reset_index(inplace=True, drop=True)
            header.columns = header.loc[0]
            header = header.drop(header.index[0])
            header.reset_index(inplace=True, drop=True)
            temp_time = time.time()
            header = self.hierarchy.get_hierarchy_id(header, curveType)
            print("time.time()-temp_time db schema", time.time() - temp_time)

            # data processing for data
            data.reset_index(drop=True, inplace=True)
            data.columns = data.iloc[0]
            data = data.drop(data.index[0])
            data['Date'] = data['Date'] + "-" + data['HE'].astype(str)
            data.drop(['HE'], axis=1, inplace=True)
            data = data.transpose()
            data.columns = data.iloc[0]
            data = data.drop(data.index[0])
            # data = data.drop([0], axis=1)
            data.reset_index(inplace=True, drop=True)
            # data = data.rename(columns = {data.columns[0]:'sub_cost_component'})
            
            merged_df = pd.merge(header, data, left_index=True, right_index=True)
            temp_time = time.time()
            melted_df = pd.melt(merged_df, id_vars=list(header.columns), var_name='date', value_name='data')
            print("time.time()-temp_time melt", time.time() - temp_time)
            # melted_df = melted_df.rename(columns=lambda x: x.strip().replace(' ', '_').lower())
            # melted_df.loc[melted_df['sub_cost_component'].apply(lambda x: isinstance(x, float)), 'sub_cost_component'] = melted_df['cost_component']
            # melted_df.drop(['lookup_id1'], axis=1, inplace=True)
            # melted_df=melted_df.sort_values("date")
            # melted_df['data'].fillna(0, inplace=True)
            # melted_df['data'] = melted_df['data'].str.replace(r'$', '', regex=False)
            # melted_df['data'] = melted_df['data'].str.replace(r'%', '', regex=False)
            melted_df['data'] = melted_df['data'].replace('$', '', regex=False)
            melted_df.reset_index(drop=True, inplace=True)
            melted_df = melted_df.rename(columns={'id':'hierarchy_id'})
            temp_time = time.time()
            melted_df[['date', 'he']] = melted_df['date'].str.split('-', expand=True)
            print("time.time()-temp_time date-hour", time.time() - temp_time)
            # temp_time = time.time()
            # melted_df[['date', 'he']] = melted_df['Date'].str.rsplit('-', n=1, expand=True)
            # print("time.time()-temp_time date-hour", time.time() - temp_time)
            # temp_time = time.time()
            # melted_df['he'] = melted_df['date'].str.slice(11, 13)  # Extract 'HH'
            # melted_df['date'] = melted_df['date'].str.slice(0, 10)  # Extract 'YYYY-MM-DD'
            # print("time.time()-temp_time date-hour", time.time() - temp_time)
            # melted_df['he'] = melted_df['date'].apply(lambda x: x.split("-")[1])
            # melted_df['date'] = melted_df['date'].apply(lambda x: x.split("-")[0])
            return melted_df
        except Exception as e:

            import traceback, sys
            print(traceback.format_exc())
            return "File Format Not Matched"
    