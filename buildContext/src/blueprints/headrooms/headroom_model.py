"""
handles all the database operations for the headrooms
"""

import jwt
import croniter
import pandas as pd
import datetime
from sqlalchemy import text
from utils.database_connection import ConnectDatabase

class HeadroomModel:

    def __init__(self, secret_key, secret_salt):
        self.secret_key = secret_key
        self.secret_salt = secret_salt
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def decode_auth_token(self, auth_token):
        """
        validate the Auth Token
        """
        try:
            response = jwt.decode(
                        auth_token, self.secret_key, algorithms=["HS256"])
            return True, response
        except:
            return False, None

    
    def get_waiting_headrooms(self):

        """
        fetch the headroom events which are pending 
        """

        query = "select * from trueprice.headroom_trigger where status = 'waiting';"
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"curvestart": row['curvestart'], "filename": row['filename']})

            return data
        except:
            return data
        
    def mark_headroom_done(self, curvestart, filename):

        """
        mark process done after applying some operations
        """

        query = f"UPDATE trueprice.headroom_trigger set status = 'processed' where curvestart = '{curvestart}' and filename ='{filename}';"
        try:
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def get_matrix_data(self, curvestart, filename):
        """
        fetches the latest matrix data from db
        """

        query = f"select * from trueprice.matrix where curvestart = '{curvestart}' and control_area_type = '{filename}';"
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                if 'Total Bundled Price' in row['sub_cost_component']:
                    data.append({"control_area_type": row['control_area_type'], "control_area": row['control_area'],
                                "state": row['state'], "load_zone": row['load_zone'],
                                "capacity_zone": row['capacity_zone'], "utility": row['utility'],
                                "strip": row['strip'], "cost_group": row['cost_group'],
                                "cost_component": row['cost_component'], "term": row['term'],
                                "beginning_date": row['beginning_date'], "load_profile": row['load_profile'],
                                "total_bundled_price": row['data'],
                                "matching_id": row["matching_id"],
                                "lookup_id": row["lookup_id"]
                                })
            return data
        except:
            return data
        
    def get_ptc_data(self, filename):
        """
        fetches the latest ptc data from db
        """


        query = f"select * from trueprice.ptc where control_area_type = '{filename}'  and curvestart = (Select curvestart from trueprice.ptc where control_area_type = '{filename}' ORDER BY curvestart DESC LIMIT 1);"
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"control_area_type": row['control_area_type'], "control_area": row['control_area'],
                             "state": row['state'], "load_zone": row['load_zone'],
                             "capacity_zone": row['capacity_zone'], "utility": row['utility'],
                             "strip": row['strip'], "cost_group": row['cost_group'],
                             "cost_component": row['cost_component'], "utility_name": row['utility_name'],
                             "load_profile": row["profile_load"],
                             "month": row['month'], "data": row['data'],
                             "matching_id": row["matching_id"],
                             "lookup_id": row["lookup_id"]
                             })
            return data
        except:
            return data
        
    def headroom_ingestion(self, df):
        """
        ingest the headroom dataframe to the database

        """
    
        try:
            
            sod = df['curvestart'].unique()[0].strftime('%Y-%m-%d') # drop time, since any update should be new
            now = df['curvestart'].unique()[0]
            eod = (df['curvestart'].unique()[0] + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

            check_query = f"""
                -- if nothing found, new data, insert it, or do one of these
                
                select exists(select 1 from trueprice.headroom where curvestart='{now}' and control_area_type='{df['control_area_type'].unique()[0]}') -- ignore, db == file based on timestamp
                UNION ALL
                select exists(select 1 from trueprice.headroom where curvestart>='{sod}' and curvestart<'{now}' and control_area_type='{df['control_area_type'].unique()[0]}') -- update, db is older
                UNION ALL
                select exists(select 1 from trueprice.headroom where curvestart>'{now}' and curvestart<'{eod}' and control_area_type='{df['control_area_type'].unique()[0]}') -- ignore, db is newer
            """
            query_result = pd.read_sql(check_query, self.engine)
            same, old_exists, new_exists = query_result.exists[0], query_result.exists[1], query_result.exists[2]

            if same: # if data already exists neglect it
                return "Data already exists based on timestamp and strip"
            
            elif not same and not new_exists and not old_exists: # if data is new then insert it
                r = df.to_sql(f"headroom", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
                if r is not None:
                    return "Data Inserted"
                return "Failed to insert"         

            elif old_exists: # if there exists old data, handle it with slowly changing dimensions
                tmp_table_name = f"headroom{df['curvestart'].unique()[0]}" # temp table to hold new csv data so we can work in SQL
                r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
                if r is None:
                    return "Unable to create data"

                with self.engine.connect() as con:
                    curveend = df.curveStart # the new data ends the old data
                    backup_query = f'''

                    
                        -- insertion to the database in history table
                            with current as (
                                -- get the current rows in the database, all of them, not just things that will change

                                select id, control_area_type, matching_id, lookup_id,  control_area, state, load_zone,
                                    capacity_zone, utility, strip, cost_group, cost_component, load_profile, headroom, headroom_prct, curvestart, ptc,
                                from trueprice.headroom where curvestart>='{sod}' and curvestart<='{eod}' and control_area_type='{df['control_area_type'].unique()[0]}'
                            ),
                            backup as (
                                -- take current rows and insert into database but with a new "curveend" timestamp

                                insert into trueprice.headroom_history (control_area_type, matching_id, lookup_id,  control_area, state, load_zone,
                                    capacity_zone, utility, strip, cost_group, cost_component, load_profile, headroom, headroom_prct, curvestart, ptc, curveend)

                                select control_area_type, matching_id, lookup_id,  control_area, state, load_zone,
                                    capacity_zone, utility, strip, cost_group, cost_component, load_profile, headroom, headroom_prct, curvestart, ptc, {curveend} as curveend
                                from current
                            ),
                            single as (
                                select curvestart from current limit 1
                            ),
                        
                        
                        -- update the existing "current" with the new "csv"
                        
                            deletion as(
                            DELETE from trueprice.headroom
                            WHERE curvestart = (select curvestart from single)

                            ),

                            updation as (
                            insert into trueprice.headroom (control_area_type, matching_id, lookup_id,  control_area, state, load_zone,
                                    capacity_zone, utility, strip, cost_group, cost_component, load_profile, headroom, headroom_prct, curvestart, ptc)

                            select control_area_type, matching_id, lookup_id,  control_area, state, load_zone,
                                    capacity_zone, utility, strip, cost_group, cost_component, load_profile, headroom, headroom_prct, curvestart, ptc
                                from trueprice.{tmp_table_name}
                            )
                        select * from trueprice.headroom;
                   
                    
                    '''        
                    # finally execute the query
                    r = con.execute(backup_query)            
                    con.execute(f"drop table trueprice.{tmp_table_name}")
                return True
            return False
        except:
            return False
        
    def latest_headroom(self, dt):
        current_date = datetime.datetime.now()
        return (
            dt.year == current_date.year and
            dt.month == current_date.month
        )

    
    def get_headrooms_data(self):
        """
        fetches the latest headroom data from db
        """
        

        regions = ['ercot', 'pjm', 'isone', 'nyiso', 'miso']
        queries = []

        for region in regions:
            query = f"""
            SELECT *
            FROM trueprice.headroom
            WHERE control_area_type = '{region}' AND curvestart = (
                SELECT curvestart
                FROM trueprice.headroom
                WHERE control_area_type = '{region}'
                ORDER BY curvestart DESC
                LIMIT 1
            )
            """
            queries.append(query)

        final_query = " UNION ".join(queries)
        data = []
        try:
            results = self.engine.execute(final_query).fetchall()
            for row in results:
                if(self.latest_headroom(row['month'])):
                    data.append({"state": row['state'], "utility": row['utility'], "load_zone": row['load_zone'],
                                "utility_price": round(float(row['ptc']),2), "retail_price": round(float(row['total_bundled_price']),2),
                                "headroom": round(float(row['headroom']),2), "headroom_prct": round(float(row['headroom_prct']),2),
                                "customer_type": row['cost_component']
                                })
            return data
        except:
            return data