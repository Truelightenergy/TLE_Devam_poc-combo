"""
Implements the Slowly Changed Dimensions to insert the data into database
"""
import datetime
import pandas as pd
from ..database_conection import ConnectDatabase


class Ercot_AncillaryData:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def pre_processing(self, df):
        """
        pre process the dataframe just a bit
        """
        fill_values = {
            col: '$0' if '$' in str(df[col]) else '0%'
            for col in df.columns
        }
        df.fillna(fill_values, inplace=True)
        df[df.columns[1:]] = df[df.columns[1:]].replace('[\$,%]', '', regex=True).astype(float)
        # date parsing
        df['Zone'] = pd.to_datetime(df['Zone'])
        return df
    
    def renaming_columns(self, df):
        """
        renaming the columns of the dataframe
        """

        df = df.rename(columns={
            'Zone':'month',
            'RRS Future':'rrs_future',
            'NS Future':'ns_future',
            'RU Future':'ru_future', 
            'RD Future':'rd_future', 
            'RD PHYS':'rd_phys',
            'NS PHYS':'ns_phys',
            'RU PHYS':'ru_phys',
            'RRS PHYS':'rrs_phys'
        })

        return df


    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """
        df = pd.read_csv(data.fileName, skiprows=2)
        df.drop(index=[0,1,2], inplace=True, axis='rows')
        # some pre processing
        df = self.pre_processing(df)
        #renaming the columns of the dataframe
        df = self.renaming_columns(df)

        df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
        df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column
        

        sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
        now = data.curveStart
        eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        check_query = f"""
            -- if nothing found, new data, insert it, or do one of these
            
            select exists(select 1 from trueprice.{data.controlArea}_ancillarydata where curvestart='{now}'and strip='{data.strip}') -- ignore, db == file based on timestamp
            UNION ALL
            select exists(select 1 from trueprice.{data.controlArea}_ancillarydata where curvestart>='{sod}' and curvestart<'{now}' and strip='{data.strip}') -- update, db is older
            UNION ALL
            select exists(select 1 from trueprice.{data.controlArea}_ancillarydata where curvestart>'{now}' and curvestart<'{eod}' and strip='{data.strip}') -- ignore, db is newer
        """
        query_result = pd.read_sql(check_query, self.engine)
        same, old_exists, new_exists = query_result.exists[0], query_result.exists[1], query_result.exists[2]
        if same: # if data already exists neglect it
            return "Data already exists based on timestamp and strip"
        
        elif not same and not new_exists and not old_exists: # if data is new then insert it
            r = df.to_sql(f"{data.controlArea}_ancillarydata", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
            if r is None:
                return "Failed to insert"            

        elif old_exists: # if there exists old data, handle it with slowly changing dimensions
            tmp_table_name = f"{data.controlArea}_ancillarydata_{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
            r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
            
            if r is None:
                return "Unable to create data"

            with self.engine.connect() as con:
                curveend = data.curveStart # the new data ends the old data

                print(data.curveStart)
                backup_query = f'''
                    with current as (
                        -- get the current rows in the database, all of them, not just things that will change

                        select id, strip, curvestart, month, rrs_future, ns_future, ru_future, rd_future, rd_phys, ns_phys, ru_phys, rrs_phys from trueprice.{data.controlArea}_ancillarydata where curvestart>='{sod}' and curvestart<='{eod}' and strip='{data.strip}'
                    ),
                    backup as (
                        -- take current rows and insert into database but with a new "curveend" timestamp

                        insert into trueprice.{data.controlArea}_ancillarydata_history (id, strip, curvestart, curveend, month, rrs_future, ns_future, ru_future, rd_future, rd_phys, ns_phys, ru_phys, rrs_phys)
                        select id, strip, curvestart, '{curveend}' as curveend, month, rrs_future, ns_future, ru_future, rd_future, rd_phys, ns_phys, ru_phys, rrs_phys
                        from current
                    ),
                    single as (
                        select curvestart from current limit 1
                    )
                    -- update the existing "current" with the new "csv"

                    update trueprice.{data.controlArea}_ancillarydata set
                    curvestart = newdata.curveStart, -- this reflects the intra update, should only be the time not the date
                    month = newdata.month,
                    rrs_future = newdata.rrs_future,
                    ns_future = newdata.ns_future,
                    ru_future = newdata. ru_future,
                    rd_future = newdata.rd_future,
                    rd_phys = newdata.rd_phys,
                    ns_phys = newdata.ns_phys,
                    ru_phys = newdata.ru_phys,
                    rrs_phys = newdata.rrs_phys
                    from 
                        trueprice.{tmp_table_name} as newdata -- our csv data
                    where 
                        trueprice.{data.controlArea}_ancillarydata.strip = newdata.strip 
                        and trueprice.{data.controlArea}_ancillarydata.month = newdata.month 
                        and trueprice.{data.controlArea}_ancillarydata.curvestart=(select curvestart from single)
                '''        
                
                
                # finally execute the query
                r = con.execute(backup_query)            
                con.execute(f"drop table trueprice.{tmp_table_name}")

        elif new_exists:
            return "Newer data in database, abort"
        else:
            return "Ingestion logic error, we should not be here"