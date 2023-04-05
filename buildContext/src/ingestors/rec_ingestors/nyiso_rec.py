"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
import datetime
from ..database_conection import ConnectDatabase

class Nyiso_Rec:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def pre_processings(self, df):
        """
        makes some pre-processing to the dataframe
        """

        df.columns = df.columns.str.replace('\.\d+', '', regex=True)
        df.columns = df.columns.astype(str) +'_'+ df.iloc[0].astype(str)
        df.columns = df.columns.str.lower()
        df = df.drop(df.index[0])

        fill_values = {
            col: '$0' if '$' in str(df[col]) else '0'
            for col in df.columns
            }
        df.fillna(fill_values, inplace=True)
        df[df.columns[2:]] = df[df.columns[2:]].replace('[\$,]', '', regex=True)
        df[df.columns[2:]]  = df[df.columns[2:]].replace('[\%,]', '', regex=True)
        df[df.columns[2:]] = df[df.columns[2:]].astype(float)
        df['ny_ey'] = pd.to_datetime(df['ny_ey'])

        return df
    
    def renaming_columns(self, df):
        """
        rename the columns accordingly
        """

        df = df.rename(columns={
            
            'ny_ey': 'month',
            df.columns[1]: 'strip'} )
        
        return df
    
    def ingestion(self, data):
        """
        Handling Ingestion for rec
        """
        try:

            df = pd.read_csv(data.fileName)
            # some pre processings
            df = self.pre_processings(df)
            # renaming columns
            df = self.renaming_columns(df)

            df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column
            # df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
            


            # using exists always return true or false versus empty/None
            sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
            now = data.curveStart
            eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

            check_query = f"""
                -- if nothing found, new data, insert it, or do one of these
                
                select exists(select 1 from trueprice.{data.controlArea}_rec where curvestart='{now}') -- ignore, db == file based on timestamp
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_rec where curvestart>='{sod}' and curvestart<'{now}') -- update, db is older
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_rec where curvestart>'{now}' and curvestart<'{eod}') -- ignore, db is newer
            """
            query_result = pd.read_sql(check_query, self.engine)
            same, old_exists, new_exists = query_result.exists[0], query_result.exists[1], query_result.exists[2]

            if same: # if data already exists neglect it
                return "Data already exists based on timestamp and strip"
            
            elif not same and not new_exists and not old_exists: # if data is new then insert it
                r = df.to_sql(f"{data.controlArea}_rec", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
                if r is not None:
                    return "Data Inserted"
                return "Failed to insert"          

            elif old_exists: # if there exists old data, handle it with slowly changing dimensions
                tmp_table_name = f"{data.controlArea}_rec{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
                r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
                if r is None:
                    return "Unable to create data"

                with self.engine.connect() as con:
                    curveend = data.curveStart # the new data ends the old data
                    backup_query = f'''
                        with current as (
                            -- get the current rows in the database, all of them, not just things that will change

                            select id, strip, curvestart, month, ny_total_cost_per_mwh, ny_class_i, ny_class_i_price,
                            ny_class_ii, ny_class_ii_price, ny_total_cost_per_mwh_zec_rate, ny_class_iii_zec, ny_class_iii_price 
                            from trueprice.{data.controlArea}_rec where curvestart>='{sod}' and curvestart<='{eod}'
                        ),
                        backup as (
                            -- take current rows and insert into database but with a new "curveend" timestamp

                            insert into trueprice.{data.controlArea}_rec_history (id, strip, curvestart, curveend,
                            month, ny_total_cost_per_mwh, ny_class_i, ny_class_i_price,
                            ny_class_ii, ny_class_ii_price, ny_total_cost_per_mwh_zec_rate,
                            ny_class_iii_zec, ny_class_iii_price)

                            select id, strip, curvestart, '{curveend}' as curveend, month, ny_total_cost_per_mwh, ny_class_i, ny_class_i_price,
                            ny_class_ii, ny_class_ii_price, ny_total_cost_per_mwh_zec_rate, ny_class_iii_zec, ny_class_iii_price
                            from current
                        ),
                        single as (
                            select curvestart from current limit 1
                        )
                        -- update the existing "current" with the new "csv"

                        update trueprice.{data.controlArea}_rec set
                        curvestart = newdata.curveStart, -- this reflects the intra update, should only be the time not the date
                        strip = newdata.strip,
                        month = newdata.month,
                        ny_total_cost_per_mwh  = newdata.ny_total_cost_per_mwh,
                        ny_class_i =  newdata.ny_class_i,
                        ny_class_i_price = newdata.ny_class_i_price,
                        ny_class_ii = newdata.ny_class_ii,
                        ny_class_ii_price = newdata.ny_class_ii_price,
                        ny_total_cost_per_mwh_zec_rate = newdata.ny_total_cost_per_mwh_zec_rate,
                        ny_class_iii_zec = newdata.ny_class_iii_zec,
                        ny_class_iii_price = newdata.ny_class_iii_price

                        from 
                            trueprice.{tmp_table_name} as newdata -- our csv data
                        where 
                            trueprice.{data.controlArea}_rec.strip = newdata.strip 
                            and trueprice.{data.controlArea}_rec.month = newdata.month 
                            and trueprice.{data.controlArea}_rec.curvestart=(select curvestart from single)
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
            return traceback.format_exc()