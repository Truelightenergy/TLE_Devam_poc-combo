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
        
    def get_matrix_data(self, curvestart):
        """
        fetches the latest matrix data from db
        """

        query = f"select * from trueprice.matrix where curvestart = '{curvestart}';"
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"control_area_type": row['control_area_type'], "control_area": row['control_area'],
                             "state": row['state'], "load_zone": row['load_zone'],
                             "capacity_zone": row['capacity_zone'], "utility": row['utility'],
                             "strip": row['strip'], "cost_group": row['cost_group'],
                             "cost_component": row['cost_component'], "term": row['term'],
                             "beginning_date": row['beginning_date'], "load_profile": row['load_profile'],
                             "total_bundled_price": row['total_bundled_price']
                             })
            return data
        except:
            return data
        
    def get_ptc_data(self):
        """
        fetches the latest ptc data from db
        """
        current_date = datetime.datetime.now()
        required_month = current_date.replace(day=1).date()

        query = f"select * from trueprice.ptc where month::date = '{required_month}'  and curvestart = (Select curvestart from trueprice.ptc ORDER BY curvestart DESC LIMIT 1);"
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
                             "month": row['month'], "data": row['data']
                             })
            return data
        except:
            return data
        
    def headroom_ingestion(self, df):
        """
        ingest the headroom dataframe to the database

        """
    
        try:
            r = df.to_sql(f"headroom", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
            if r is not None:
                return True
            return False
        except:
            return False
    
    def get_headrooms_data(self):
        """
        fetches the latest headroom data from db
        """
        

        query = f"select * from trueprice.headroom where curvestart = (Select curvestart from trueprice.headroom ORDER BY curvestart DESC LIMIT 1);"
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"state": row['state'], "load_zone": row['load_zone'], "utility": row['utility'],
                             "headroom": row['headroom'], "headroom_prct": row['headroom_prct']
                             })
            return data
        except:
            return data