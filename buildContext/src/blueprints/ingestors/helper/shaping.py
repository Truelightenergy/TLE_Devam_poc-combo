"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
import datetime
from ..ingestor_model import IngestorUtil
from utils.configs import read_config
from ...hierarchy_utils.utils_shaping import BaseTableHierarchy
import time
import logging

config = read_config()
logging.basicConfig(level=logging.INFO)

class Shaping:
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
            df['year'] = df['year'].astype(int)
            df['datemonth'] = df['datemonth'].astype(int)
            df['weekday'] = df['weekday'].astype(int)
            df['he'] = df['he'].astype(int)
            df.rename(inplace=True, columns={
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
            
                select exists(select 1 from trueprice.{data.controlArea}_{data.curveType} where curvestart='{now}') -- ignore, "db == file" based on timestamp
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_{data.curveType} where curvestart>='{sod}' and curvestart<='{now}') -- update, db already exists
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_{data.curveType} where curvestart>='{now}' and curvestart<'{eod}' ) -- ignore, db is equal or newer
            """
            r = pd.read_sql(check_query, self.db_util.engine)
            same, old_exists, new_exists = r.exists[0], r.exists[1], r.exists[2]

            if same: # if data already exists neglect it
                return "Insert aborted, data already exists based on timestamp and strip"
            elif new_exists:
                return "Insert aborted, newer data in database"
            elif not same and not new_exists and not old_exists: # upsert new data
                r = df.to_sql(f"{data.controlArea}_{data.curveType}", con = self.db_util.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
                if r is not None:
                    return "Data Inserted"
                return "Insert aborted, failed to insert new data"
                    
            elif old_exists: # perform scd-2
                tmp_table_name = f"{data.controlArea}_{data.curveType}_{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
                r = df.to_sql(f'{tmp_table_name}', con = self.db_util.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
                if r is None:
                    return "Unable to create temp data table for update"
                            

                with self.db_util.engine.connect() as con:
                    curveend = data.curveStart # the new data ends the old data
                    backup_query = f'''

                    
                        -- insertion to the database in history table
                            with current as (
                                -- get the current rows in the database, all of them, not just things that will change

                                select id, month, curvestart, data, hierarchy_id, year, datemonth, weekday, he
                                from trueprice.{data.controlArea}_{data.curveType} where curvestart>='{sod}' and curvestart<='{eod}'
                            ),
                            backup as (
                                -- take current rows and insert into database but with a new "curveend" timestamp

                                insert into trueprice.{data.controlArea}_{data.curveType}_history ( month, curvestart, curveend, data, hierarchy_id, year, datemonth, weekday, he)

                                select  month, curvestart, '{curveend}' as curveend, data, hierarchy_id, year, datemonth, weekday, he
                                from current
                            ),
                            single as (
                                select curvestart from current limit 1
                            ),
                        
                        
                        -- update the existing "current" with the new "csv"
                        
                            deletion as(
                            DELETE from trueprice.{data.controlArea}_{data.curveType}
                            WHERE curvestart = (select curvestart from single)

                            ),

                            updation as (
                            insert into trueprice.{data.controlArea}_{data.curveType} ( month, curvestart, data, hierarchy_id, year, datemonth, weekday, he)

                            select  month, curvestart, data, hierarchy_id, year, datemonth, weekday, he
                                from trueprice.{tmp_table_name}
                            )
                        select * from trueprice.{data.controlArea}_{data.curveType};
                   
                    
                    '''          
                

                    # finally execute the query
                    r = con.execute(backup_query)
                    con.execute(f"drop table trueprice.{tmp_table_name}")
                return "Data updated"
            else:
                return "Unknown insert/update error"
        except Exception as exp:
            import traceback, sys
            print(traceback.format_exc())
            print("Error in data dump: ", exp)
            logging.info(exp)
            return "Failure in Ingestion"
    
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
            # data.columns = data.iloc[0]
            data = data.drop(data.index[0])
            base_list = [0, 1, 2, 3, 4]
            data_list = data.columns.difference(base_list)
            temp_time = time.time()
            dataframes = [data[base_list + [col]].assign(hierarchy_id=header.iloc[i].id).rename(columns={col: 'data'})
              for i, col in enumerate(data_list)]
            melted_df = pd.concat(dataframes)
            melted_df.rename(columns={0:"date", 1:"year", 2:"datemonth", 3:"weekday", 4:'he'}, inplace=True)
            print("time.time()-temp_time melt", time.time() - temp_time)
            melted_df['data'] = melted_df['data'].replace('$', '', regex=False)
            melted_df.reset_index(drop=True, inplace=True)
            return melted_df
        except Exception as e:

            import traceback, sys
            print(traceback.format_exc())
            return "File Format Not Matched"