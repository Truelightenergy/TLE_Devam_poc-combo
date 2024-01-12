"""
Managing Database Operations
"""
import jwt
import datetime
import hashlib
from utils.database_connection import ConnectDatabase
from utils.configs import read_config

config = read_config()

class DataBaseUtils:
    """
    Managing Database operations
    """

    def __init__(self, secret_key, secret_salt):
        """
        connection database here 
        """

        self.secret_key = secret_key
        self.secret_salt = secret_salt
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

        
    def change_password(self, email, new_password):
        """
        allowing user to change his password
        """
        try:
            query = f"UPDATE trueprice.users SET password = '{new_password}' WHERE email = '{email}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def verify_api(self):
        """
        verify api is enabled
        """
        try:
            query = f" SELECT * from trueprice.site  WHERE admin='tle_admin' AND api_status ='enabled';"
            results = self.engine.execute(query).fetchall()
            flag = False
            for row in results:
                flag = True
            return flag
        except:
            return False
        
    def verify_ui(self):
        """
        verify ui is enabled
        """
        try:
            query = f" SELECT * from trueprice.site  WHERE admin='tle_admin' AND ui_status ='enabled';"
            results = self.engine.execute(query).fetchall()
            flag = False
            for row in results:
                flag = True
            return flag
        except:
            return False
          
    
    
        
    def decode_auth_token(self, auth_token):
        """
        validate the Auth Token
        """
        try:
            response = jwt.decode(
                        auth_token, self.secret_key, algorithms=[config['hash_algo']])
            return True, response
        except:
            return False, None
        


    def verify_user_status(self, client_email):
        """
        authenticate user before request
        """
        try:
            
            query = f"SELECT * FROM trueprice.users WHERE email = '{client_email}' AND status = 'enabled';"

            results = self.engine.execute(query).fetchall()
            flag = False
            for row in results:
                flag = True
                break
            return flag
        except:
            return False
        
        
    def get_user_current_role(self, email):
        """
        on the basis of email it returns  back the user role
        """

        try:
            query = f"select * from trueprice.users where email='{email}';"
            results = self.engine.execute(query).fetchall()
            role = None
            for row in results:
                role = row['privileged_level']
                break
            return role
        
        except:
            return None

    def get_table_columns(self, curve, iso):
        """
        get the data for all the columns of any table
        """
        
        try :
            query = f"""
                SELECT DISTINCT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                FROM trueprice.{iso}_{curve};
            """

            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
            

    def add_column_authorization(self, email, table,  startMonth, endMonth, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component):
        """
        creating a new user for now
        """
        try:
            query = f"""
                INSERT INTO trueprice.column_authorization (email, control_table, startMonth, endMonth, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component)
                VALUES ('{email}', {table}, '{startMonth}', '{endMonth}', '{control_area}', '{state}', '{load_zone}', '{capacity_zone}', '{utility}', '{strip}', '{cost_group}', '{cost_component}', '{sub_cost_component}');
            """
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        
    def update_column_authorization(self, email, table, startMonth, endMonth, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component):
        """
        creating a new user for now
        """
        try:
            query = f"""
                UPDATE trueprice.column_authorization
                SET email = '{email}',
                    table = '{table},
                    control_area = '{control_area}',
                    startMonth = '{startMonth}',
                    endMonth = '{endMonth}',
                    state = '{state}',
                    load_zone = '{load_zone}',
                    capacity_zone = '{capacity_zone}',
                    utility = '{utility}',
                    strip = '{strip}',
                    cost_group = '{cost_group}',
                    cost_component = '{cost_component}',
                    sub_cost_component = '{sub_cost_component}'
                WHERE email = '{email}' 
                    AND control_table = '{table}'
                    AND control_area = '{control_area}'
                    AND state = '{state}'
                    AND load_zone = '{load_zone}'
                    AND capacity_zone = '{capacity_zone}'
                    AND utility = '{utility}'
                    AND strip = '{strip}'
                    AND cost_group = '{cost_group}'
                    AND cost_component = '{cost_component}'
                    AND sub_cost_component = '{sub_cost_component}';
            """

            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        
    
            

    

    

        
    

        


