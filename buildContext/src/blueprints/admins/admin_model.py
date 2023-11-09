"""
creates the model of the admin operations
"""
import jwt
import hashlib
import datetime
from sqlalchemy import text
from utils.database_connection import ConnectDatabase
from sqlalchemy.orm import sessionmaker, relationship
            

class AdminUtil:

    """
    creates the model of the admin operations
    """

    def __init__(self, secret_key, secret_salt):
        """
        connection database here 
        """

        self.secret_key = secret_key
        self.secret_salt = secret_salt
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

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
        

    def view_authorized_columns_from_api(self, email):
        """
        extracts all the uploads from the database
        """
        try:
            query = f"""
                SELECT id, control_table, email, startMonth::timestamp::date, endMonth::timestamp::date, balanced_month_range, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                FROM trueprice.column_authorization
                WHERE email = '{email}';
            """
            data = list()        
            response = self.engine.execute(query).fetchall()
            for row in response:

                results = {
                "control_table":row['control_table'],
                "email": row["email"],
                "startMonth": row["startmonth"],
                "endMonth": row["endmonth"],
                "balanced_month_range": row['balanced_month_range'],
                "control_area" : row["control_area"],
                "state" : row["state"],
                "load_zone" : row['load_zone'],
                "capacity_zone" : row['capacity_zone'],
                "utility" : row["utility"],
                "strip" : row["strip"],
                "cost_group" : row["cost_group"], 
                "cost_component" : row["cost_component"], 
                "sub_cost_component" : row["sub_cost_component"]
            }     
                data.append(results)      


            return data
        except:
            return None
    def view_authorized_columns_from_ui(self, user_id):
        """
        extracts all the uploads from the database
        """
        try:
            query = f"""
                SELECT id, control_table, email, startMonth::timestamp::date, endMonth::timestamp::date, balanced_month_range, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                FROM trueprice.column_authorization
                WHERE email = (select email from trueprice.users WHERE id={user_id});
            """
            id = []
            table = []
            emails = []
            start = []
            end = []
            months =[]
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
                months.append(row['balanced_month_range'])
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
                "balanced_month_range": months,
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
        
    def ingest_filter_rule(self, query_strings):
        """
        insert the new rule into database for data
        """

        try:
            
            query = f"INSERT INTO trueprice.column_authorization (email, control_table,  startMonth, endMonth, balanced_month_range, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component) VALUES ('{query_strings['user']}', '{query_strings['control_table']}', '{query_strings['start']}', '{query_strings['end']}', '{query_strings['balanced_month']}', '{query_strings['control_area']}', '{query_strings['state']}', '{query_strings['load_zone']}', '{query_strings['capacity_zone']}', '{query_strings['utility']}', '{query_strings['strip']}', '{query_strings['cost_group']}', '{query_strings['cost_component']}', '{query_strings['sub_cost_component']}');"
        
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        
        
    def remove_previous_filter_rule(self, query_strings):
        """
        insert the new rule into database for data
        """

        try:
            
            query = f"DELETE FROM trueprice.column_authorization WHERE email = '{query_strings['user']}' AND control_table = '{query_strings['control_table']}' AND control_area = '{query_strings['control_area']}' AND state = '{query_strings['state']}' AND load_zone = '{query_strings['load_zone']}' AND capacity_zone = '{query_strings['capacity_zone']}' AND utility = '{query_strings['utility']}' AND strip = '{query_strings['strip']}' AND cost_group = '{query_strings['cost_group']}'AND cost_component = '{query_strings['cost_component']}' AND sub_cost_component = '{query_strings['sub_cost_component']}';"
        
            result = self.engine.execute(query)
            if result.rowcount >=0:
                return True
            return False
        except :
            return False
        
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

    def get_user_authorized_columns(self, user_id):
        """
        get the data for all the columns of any table
        """
        
        try :
            query = f"""
                SELECT id, control_table,  email, startMonth::timestamp::date, endMonth::timestamp::date, balanced_month_range, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component 
                FROM trueprice.column_authorization
                WHERE email = (select email from trueprice.users WHERE id={user_id});
            """
            results = self.engine.execute(query).fetchall()
            return results
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
        query = text(query)
        try:
            results = self.engine.execute(query).fetchall()
            sub_cost_components = []
            for row in results:
                sub_cost_components.append(row['sub_cost_component'])
            return sub_cost_components
        except:
            import traceback, sys
            print(traceback.format_exc())
            return None
        
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
    
        

    def get_catalog_data_from_db(self):
        """
        extracts thw whole catalog data at once
        """
       

        tables = ["ercot_energy", "nyiso_energy", "miso_energy", "isone_energy", "pjm_energy",
                  "ercot_nonenergy", "nyiso_nonenergy", "miso_nonenergy", "isone_nonenergy", "pjm_nonenergy",
                  "ercot_rec", "nyiso_rec", "isone_rec", "pjm_rec"
                  ]
        states_responses = dict()
        curve_responses = {"energy": dict(), "nonenergy": dict(), "rec": dict()}
        try:
            for table in tables:
                
                single_response = list()
                control_areas =  self.get_control_area_for_dropdown(table)
                for c_area in control_areas:
                    states = self.get_state_for_dropdown(table, c_area)
                    for st in states:
                        load_zones = self.get_load_zone_for_dropdown(table, c_area, st)
                        for l_zone in load_zones:
                            capacity_zones = self.get_capacity_zone_for_dropdown(table, c_area, st, l_zone)
                            for c_zone in capacity_zones:
                                utilities = self.get_utility_for_dropdown(table, c_area, st, l_zone, c_zone)
                                for util in utilities:
                                    strips = self.get_block_type_for_dropdown(table, c_area, st, l_zone, c_zone, util)
                                    for strip in strips:
                                        cost_groups = self.get_cost_group_for_dropdown(table, c_area, st, l_zone, c_zone, util, strip)
                                        for c_group in cost_groups:
                                            cost_components = self.get_cost_components_for_dropdown(table, c_area, st, l_zone, c_zone, util, strip, c_group)
                                            for c_comp in cost_components:
                                                sub_cost_component = self.get_sub_cost_components_for_dropdown (table, c_area, st, l_zone, c_zone, util, strip, c_group, c_comp)
                                                single_response.extend([
                                                    {
                                                        "control_area": c_area,
                                                        "state": st,
                                                        "load_zone": l_zone,
                                                        "capacity_zone": c_zone,
                                                        "utility": util,
                                                        "block_type": strip,
                                                        "cost_group": c_group,
                                                        "cost_component": c_comp,
                                                        "sub_cost_component": sc_comp
                                                    }
                                                    for sc_comp in sub_cost_component
                                                ])


                # states_responses[table.split("_")[0]] = single_response
                curve_responses[table.split("_")[1]][table.split("_")[0]] = single_response
                
            return curve_responses
        except :
            import traceback, sys
            print(traceback.format_exc())
            return None
        
    def ingest_multiple_filters(self, filters, user_email):
        """
        insert all rules into databases for data
        """

        try:
            base_query = "INSERT INTO trueprice.column_authorization (email, control_table, startMonth, endMonth, balanced_month_range, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component) VALUES"
            values = []
            for query_strings in filters:
                value_set = f"('{query_strings['user']}', '{query_strings['control_table']}', '{query_strings['start']}', '{query_strings['end']}', '{query_strings['balanced_month']}', '{query_strings['control_area']}','{query_strings['state']}', '{query_strings['load_zone']}', '{query_strings['capacity_zone']}', '{query_strings['utility']}', '{query_strings['block_type']}', '{query_strings['cost_group']}', '{query_strings['cost_component']}', '{query_strings['sub_cost_component']}')"
                values.append(value_set)
           
            self.session.begin()
            query = base_query + ", ".join(values)
            query = text(query)

            deletion_query = f"""
                DELETE FROM trueprice.column_authorization
                WHERE email = '{user_email}';
            """

            result = self.engine.execute(deletion_query)
            result = self.engine.execute(query)
            self.session.commit()
            if result.rowcount > 0:
                return True
            self.session.rollback()
            return False
        except :
            self.session.rollback()
            return False
        
    def remove_all_subscription(self, user_id):
        """
        remove all subscription for all the users
        """
        try:
            query = f"""
                DELETE FROM trueprice.column_authorization
                WHERE email = (select email from trueprice.users WHERE id={user_id});
            """
            result = self.engine.execute(query)
            if result.rowcount >= 0:
                return True
            return False
        except :
            return False