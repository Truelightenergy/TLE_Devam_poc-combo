"""
Managing Database Operations
"""
import jwt
import datetime
import hashlib
from database_connection import ConnectDatabase

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

    def create_user(self, client_email, client_password, level):
        """
        creating a new user for now
        """

        try:
            salted_password = self.secret_salt + client_password 
            hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
            query = f"INSERT INTO trueprice.users(email, password, privileged_level) VALUES ('{client_email}', '{hashed_salted_password}', '{level}');"
        
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
            
    def authenticate_user(self, client_email, client_password):
        """
        authenticate user based on given credentials
        """
        try:
            salted_password = self.secret_salt + client_password 
            hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
            query = f"SELECT * FROM trueprice.users WHERE email = '{client_email}' AND password = '{hashed_salted_password}' AND status = 'enabled';"

            results = self.engine.execute(query).fetchall()
            flag = False
            admin_check = False
            for row in results:
                flag = True
                admin_check = row['privileged_level']
            return flag, admin_check
        except:
            return False, False
        
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
          
    def encode_auth_token(self, client_email, client_password, client_role):
        """
        Generates the Auth Token
        
        """

        try:
            salted_password = self.secret_salt + client_password 
            hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
        
            payload = {'client_email': client_email, 
                        'client_password' : hashed_salted_password,
                        'role': client_role,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}
            token = jwt.encode(payload,
                        self.secret_key, "HS256")
            return True, token
        except:
            return False, None
    
        
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
        
    def get_all_users(self):
        """
        extracts all the users from the database
        """
        query = f"SELECT * FROM trueprice.users;"

        try:
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
        
    def get_all_users_data(self):
        """
        extracts all the users from the database
        """
        try:
            query = f"SELECT * FROM trueprice.users;"
            emails = []
            levels = []
        
            response = self.engine.execute(query).fetchall()
            for row in response:
                emails.append(row["email"])
                levels.append(row["privileged_level"])
            results = {
                "email": emails,
                "privileged_level": levels
            }


            return results
        except:
            return None
    def get_all_uploads(self):
        """
        extracts all the uploads from the database
        """
        query = f"""
            WITH t AS (
                SELECT * FROM trueprice.uploads ORDER BY timestamp DESC LIMIT 10
            )
            SELECT * FROM t ORDER BY timestamp ASC;
        """

        try:
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
    def get_all_uploads_data(self):
        """
        extracts all the uploads from the database
        """
        try:
            query = f"""
                WITH t AS (
                    SELECT * FROM trueprice.uploads ORDER BY timestamp DESC LIMIT 10
                )
                SELECT * FROM t ORDER BY timestamp ASC;
            """
            emails = []
            filenames = []
            timestamps =[]
        
            response = self.engine.execute(query).fetchall()
            for row in response:
                emails.append(row["email"])
                filenames.append(row["filename"])
                timestamps.append(row["timestamp"])

            results = {
                "email": emails,
                "files": filenames,
                "timestamps": timestamps
            }


                
            return results
        except:
            return None
        
    
        
        
        
    def get_user(self, user_id):
        """
        extracts all the users from the database
        """
        try:
            query = f"SELECT * FROM trueprice.users where id = {user_id};"
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
        
    
    def enable_disable_user(self, user_id, status):
        """
        disables or enables user based on thier id
        """
        try:
            query = f"UPDATE trueprice.users SET status = '{status}' WHERE id={user_id};"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def enable_disable_user_using_email(self, user_email, status):
        """
        disables or enables user based on their emails
        """

        try:
            query = f"UPDATE trueprice.users SET status = '{status}'  WHERE email='{user_email}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
        
    def update_user(self, user_id, prv_level):
        """
        update user inside the application
        """
        try:
            query = f"UPDATE trueprice.users SET privileged_level = '{prv_level}' WHERE id={user_id};"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def update_user_using_email(self, user_email, prv_level):
        """
        update user from the api
        """
        try:
            query = f"UPDATE trueprice.users SET privileged_level = '{prv_level}' WHERE email='{user_email}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False

        
    def update_password(self, old_pswd, new_pswd, email):
        """
        update the password
        """
        try:
            old_salted_password = self.secret_salt + old_pswd 
            hashed_old_salted_password = hashlib.sha512(old_salted_password.encode()).hexdigest()

            new_salted_password = self.secret_salt + new_pswd 
            hashed_new_salted_password = hashlib.sha512(new_salted_password.encode()).hexdigest()
            

            query = f"UPDATE trueprice.users SET password = '{hashed_new_salted_password}' WHERE email='{email}' and password ='{hashed_old_salted_password}';"

            
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False


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
        
    def save_log(self,time_stamp, email, filename):
        """
        make a log for uploaded file
        """
        try:
            query = f"INSERT INTO trueprice.uploads(timestamp, email, filename) VALUES ('{time_stamp}', '{email}', '{filename}');"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False

    def get_site_controls(self):
        """
        authenticate user before request
        """
        
        query = f"SELECT * FROM trueprice.site;"
        try:
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        

    def get_site_controls_data(self):
        """
        extracts all the site from the database
        """
        try:
            query = f"SELECT * FROM trueprice.site;"
            ui = []
            api = []
        
            response = self.engine.execute(query).fetchall()
            for row in response:
                ui.append(row["ui_status"])
                api.append(row["api_status"])
            results = {
                "UI_status": ui,
                "API_status": api
            }


            return results
        except:
            return None

        
        
    def switch_api(self, status):
        """
        switch enable or disable
        """
        if status not in ["enabled", "disabled"]:
            status = "enabled"

        try:
            query = f"UPDATE trueprice.site SET api_status = '{status}'  WHERE admin='tle_admin';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def switch_ui(self, status):
        """
        switch enable or disable
        """
        if status not in ["enabled", "disabled"]:
            status = "enabled"

        try:
            query = f"UPDATE trueprice.site SET ui_status = '{status}'  WHERE admin='tle_admin';"
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
        
    def get_user_email(self, user_id):
        """
        get email of user based on the id
        """

        try:
            query = f"select * from trueprice.users where id={user_id};"
            results = self.engine.execute(query).fetchall()
            mail = None
            for row in results:
                mail = row['email']
                break
            return mail
        
        except:
            return None
        
    def reset_user_password(self, user_id, password):
        """
        reset users password
        """

        salted_password = self.secret_salt + password 
        hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()

        try:
            query = f"UPDATE trueprice.users SET password = '{hashed_salted_password}' WHERE id = {user_id};"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def reset_user_password_for_api(self, email):
        """
        reset users password
        """

        salted_password = self.secret_salt + email 
        hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()

        try:
            query = f"UPDATE trueprice.users SET password = '{hashed_salted_password}' WHERE email = '{email}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        

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
        

    def get_user_authorized_columns(self, user_id):
        """
        get the data for all the columns of any table
        """
        
        try :
            query = f"""
                SELECT id, control_table,  email, startMonth::timestamp::date, endMonth::timestamp::date, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                FROM trueprice.column_authorization
                WHERE email = (select email from trueprice.users WHERE id={user_id});
            """
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
    def view_authorized_columns_from_api(self, email):
        """
        extracts all the uploads from the database
        """
        try:
            query = f"""
                SELECT id, control_table, email, startMonth::timestamp::date, endMonth::timestamp::date, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                FROM trueprice.column_authorization
                WHERE email = '{email}';
            """
            id = []
            table = []
            emails = []
            start = []
            end = []
            control_area = []
            state = []
            load_zone = []
            capacity_zone = []
            utility = []
            strip = []
            cost_group = []
            cost_component = []
            sub_cost_component = []

        
            response = self.engine.execute(query).fetchall()
            for row in response:
                id.append(row["id"])
                table.append(row['control_table'])
                emails.append(row["email"])
                start.append(row["startmonth"])
                end.append(row["endmonth"])
                control_area.append(row["control_area"])
                state.append(row["state"])
                load_zone.append(row["load_zone"])
                capacity_zone.append(row["capacity_zone"])
                utility.append(row["utility"])
                strip.append(row["strip"])
                cost_group.append(row["cost_group"])
                cost_component.append(row["cost_component"])
                sub_cost_component.append(row["sub_cost_component"])

            results = {
                "id": id,
                'control_table':table,
                "email": emails,
                "startMonth": start,
                "endMonth": end,
                "control_area" : control_area,
                "state" : state,
                "load_zone" : load_zone,
                "capacity_zone" : capacity_zone,
                "utility" : utility,
                "strip" : strip,
                "cost_group" : cost_group, 
                "cost_component" : cost_component, 
                "sub_cost_component" : sub_cost_component
            }


            return results
        except:
            return None
        
    def view_authorized_columns_from_ui(self, user_id):
        """
        extracts all the uploads from the database
        """
        try:
            query = f"""
                SELECT id, control_table, email, startMonth::timestamp::date, endMonth::timestamp::date, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                FROM trueprice.column_authorization
                WHERE email = (select email from trueprice.users WHERE id={user_id});
            """
            id = []
            table = []
            emails = []
            start = []
            end = []
            control_area = []
            state = []
            load_zone = []
            capacity_zone = []
            utility = []
            strip = []
            cost_group = []
            cost_component = []
            sub_cost_component = []

        
            response = self.engine.execute(query).fetchall()
            for row in response:
                id.append(row["id"])
                table.append(row['control_table'])
                emails.append(row["email"])
                start.append(row["startmonth"])
                end.append(row["endmonth"])
                control_area.append(row["control_area"])
                state.append(row["state"])
                load_zone.append(row["load_zone"])
                capacity_zone.append(row["capacity_zone"])
                utility.append(row["utility"])
                strip.append(row["strip"])
                cost_group.append(row["cost_group"])
                cost_component.append(row["cost_component"])
                sub_cost_component.append(row["sub_cost_component"])

            results = {
                "id": id,
                "control_table": table,
                "email": emails,
                "startMonth": start,
                "endMonth": end,
                "control_area" : control_area,
                "state" : state,
                "load_zone" : load_zone,
                "capacity_zone" : capacity_zone,
                "utility" : utility,
                "strip" : strip,
                "cost_group" : cost_group, 
                "cost_component" : cost_component, 
                "sub_cost_component" : sub_cost_component
            }


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
        
    
        

    def delete_auth_column_filter(self, filter_id):
        """
        remove auth filter
        """
        
        try:
            query = f"DELETE FROM trueprice.column_authorization WHERE id = {filter_id};"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def get_userid_from_filter_auth_id(self, filter_id):
        """
        get the data for all the columns of any table
        """
        
        try :
            query = f"""
                SELECT id
                FROM trueprice.users
                WHERE email = (select email from trueprice.column_authorization WHERE id={filter_id});
            """
            results = self.engine.execute(query).fetchall()
            id = None
            for row in results:
                id = row['id']
                break
            return id
        except:
            return None
        
    def get_all_users_for_dropdown(self):
        """
        extracts all the users from the database
        """
        query = f"SELECT * FROM trueprice.users WHERE privileged_level='read_write_user' OR privileged_level='read_only_user';"

        try:
            results = self.engine.execute(query).fetchall()
            users = []
            for row in results:
                users.append(row['email'])
            return users
        except:
            return None
        
    def get_control_area_for_dropdown(self, table):
        """
        extracts all the control area from the database
        """
        query = f"SELECT DISTINCT(control_area) FROM trueprice.{table};"

        try:
            results = self.engine.execute(query).fetchall()
            control_area = []
            for row in results:
                control_area.append(row['control_area'])
            return control_area
        except:
            return None
        

    def get_state_for_dropdown(self, table, control_area):
        """
        extracts all the state from the database
        """
        query = f"SELECT DISTINCT(state) FROM trueprice.{table} WHERE control_area = '{control_area}';"

        try:
            results = self.engine.execute(query).fetchall()
            states = []
            for row in results:
                states.append(row['state'])
            return states
        except:
            return None
        
    def get_load_zone_for_dropdown(self, table, control_area, state):
        """
        extracts all the load zone from the database
        """
        query = f"SELECT DISTINCT(load_zone) FROM trueprice.{table} WHERE control_area = '{control_area}' AND state = '{state}';"

        try:
            results = self.engine.execute(query).fetchall()
            zones = []
            for row in results:
                zones.append(row['load_zone'])
            return zones
        except:
            return None
        

    def get_capacity_zone_for_dropdown(self, table, control_area, state, load_zone):
        """
        extracts all the capacity zone from the database
        """
        query = f"SELECT DISTINCT(capacity_zone) FROM trueprice.{table} WHERE control_area = '{control_area}' AND state = '{state}' AND load_zone = '{load_zone}';"

        try:
            results = self.engine.execute(query).fetchall()
            zones = []
            for row in results:
                zones.append(row['capacity_zone'])
            return zones
        except:
            return None
    

    def get_utility_for_dropdown(self, table, control_area, state, load_zone, capacity_zone):
        """
        extracts all the utility from the database
        """
        query = f"SELECT DISTINCT(utility) FROM trueprice.{table} WHERE control_area = '{control_area}' AND state = '{state}' AND load_zone = '{load_zone}' AND capacity_zone ='{capacity_zone}';"

        try:
            results = self.engine.execute(query).fetchall()
            utilities = []
            for row in results:
                utilities.append(row['utility'])
            return utilities
        except:
            return None
        
    def get_block_type_for_dropdown(self, table, control_area, state, load_zone, capacity_zone, utility):
        """
        extracts all the block type from the database
        """
        query = f"SELECT DISTINCT(strip) FROM trueprice.{table} WHERE control_area = '{control_area}' AND state = '{state}' AND load_zone = '{load_zone}' AND capacity_zone ='{capacity_zone}' AND utility = '{utility}';"

        try:
            results = self.engine.execute(query).fetchall()
            strips = []
            for row in results:
                strips.append(row['strip'])
            return strips
        except:
            return None
        
    def get_cost_group_for_dropdown(self, table, control_area, state, load_zone, capacity_zone, utility, strip):
        """
        extracts all the cost group from the database
        """
        query = f"SELECT DISTINCT(cost_group) FROM trueprice.{table} WHERE control_area = '{control_area}' AND state = '{state}' AND load_zone = '{load_zone}' AND capacity_zone ='{capacity_zone}' AND utility = '{utility}' AND strip = '{strip}';"

        try:
            results = self.engine.execute(query).fetchall()
            cost_groups = []
            for row in results:
                cost_groups.append(row['cost_group'])
            return cost_groups
        except:
            return None
        
    def get_cost_components_for_dropdown(self, table, control_area, state, load_zone, capacity_zone, utility, strip, cost_group):
        """
        extracts all the cost components from the database
        """
        query = f"SELECT DISTINCT(cost_component) FROM trueprice.{table} WHERE control_area = '{control_area}' AND state = '{state}' AND load_zone = '{load_zone}' AND capacity_zone ='{capacity_zone}' AND utility = '{utility}' AND strip = '{strip}' AND cost_group= '{cost_group}';"

        try:
            results = self.engine.execute(query).fetchall()
            cost_components = []
            for row in results:
                cost_components.append(row['cost_component'])
            return cost_components
        except:
            return None
        
    def get_sub_cost_components_for_dropdown(self, table, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component):
        """
        extracts all the sub cost component from the database
        """
        query = f"SELECT DISTINCT(sub_cost_component) FROM trueprice.{table} WHERE control_area = '{control_area}' AND state = '{state}' AND load_zone = '{load_zone}' AND capacity_zone ='{capacity_zone}' AND utility = '{utility}' AND strip = '{strip}' AND cost_group= '{cost_group}' AND cost_component = '{cost_component}';"

        try:
            results = self.engine.execute(query).fetchall()
            sub_cost_components = []
            for row in results:
                sub_cost_components.append(row['sub_cost_component'])
            return sub_cost_components
        except:
            return None
        

    def ingest_filter_rule(self, query_strings):
        """
        insert the new rule into database for data
        """

        try:
            
            query = f"INSERT INTO trueprice.column_authorization (email, control_table,  startMonth, endMonth, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component) VALUES ('{query_strings['user']}', '{query_strings['control_table']}', '{query_strings['start']}', '{query_strings['end']}', '{query_strings['control_area']}', '{query_strings['state']}', '{query_strings['load_zone']}', '{query_strings['capacity_zone']}', '{query_strings['utility']}', '{query_strings['strip']}', '{query_strings['cost_group']}', '{query_strings['cost_component']}', '{query_strings['sub_cost_component']}');"
        
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        
    def check_filter_rule(self, query_strings):
        """
        insert the new rule into database for data
        """

        try:
            
            query = f"select * from trueprice.column_authorization WHERE email = '{query_strings['user']}' AND control_table = '{query_strings['control_table']}' AND control_area = '{query_strings['control_area']}' AND state = '{query_strings['state']}' AND load_zone = '{query_strings['load_zone']}' AND capacity_zone = '{query_strings['capacity_zone']}' AND utility = '{query_strings['utility']}' AND strip = '{query_strings['strip']}' AND cost_group = '{query_strings['cost_group']}'AND cost_component = '{query_strings['cost_component']}' AND sub_cost_component = '{query_strings['sub_cost_component']}';"
        
            result = self.engine.execute(query)
            if result.rowcount == 0:
                return True
            return False
        except :
            return False

    

        
    

        


