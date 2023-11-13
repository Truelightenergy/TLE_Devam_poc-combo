"""
handles all the database operations for graph view
"""
import jwt
import datetime
import pandas as pd
from sqlalchemy import text
from utils.database_connection import ConnectDatabase

class GraphView_Util:
    """
    handles all the database operations for graph view
    """

    def __init__(self, secret_key, secret_salt):
        """
        initiate the constructor
        """
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


    def get_locations_data(self, table):
        """
        extracts all the sub cost components from the database
        """
        query = f"select DISTINCT(sub_cost_component) FROM trueprice.{table} where strip='5x16';"

        try:
            results = self.engine.execute(query).fetchall()
            locations = []
            for row in results:
                locations.append(row['sub_cost_component'])
            return locations
        except:
            return None
        
    def get_data(self, table, location, start_date, end_date, operating_day, history, cob, operatin_day_timestamp):
        """
        extracts the data from the database based on the given filters
        """

        curvestartfilter = f"and curvestart::date = '{operating_day}'"

        tableName = table

        if history == 'true':
            tableName = tableName + '_history'
            curvestartfilter = f"and date_trunc('minute',curvestart) = '{operatin_day_timestamp}'::timestamp"

        query = f"""select month::date, data FROM trueprice.{tableName} 
                        where strip='5x16' and sub_cost_component='{location}' 
                        and month::date >= '{start_date}' 
                        and month::date <= '{end_date}' 
                        {curvestartfilter}
                        and cob = {cob=='true'} 
                        order by month::date;"""
        
        data_frame = pd.read_sql_query(sql=query, con=self.engine.connect())
        data_frame.sort_values(by='month', inplace = True)
        return data_frame

    def get_intraday_timestamps(self, table, operating_day, strip):
        """
        extracts all the intraday timestamps and their history status from the database
        """
        query = f"""
            SELECT distinct curvestart, true as history FROM trueprice.{table}_history 
            WHERE curvestart::date = '{operating_day}' AND strip='{strip}'
            UNION 
            SELECT distinct curvestart, false as history FROM trueprice.{table} 
            WHERE curvestart::date = '{operating_day}' AND strip='{strip}';
        """

        try:
            results = self.engine.execute(query).fetchall()
            timestamps = [{'timestamp': row['curvestart'].strftime('%Y-%m-%d %H:%M'), 'history': row['history']} for row in results]
            return timestamps
        except:
            return None


    def get_load_zones(self,table,strip):
        """
        extracts all the load zones from the database
        """
        query = f"select DISTINCT(load_zone) FROM trueprice.{table} where strip='{strip}';"

        try:
            results = self.engine.execute(query).fetchall()
            loadZones = []
            for row in results:
                loadZones.append(row['load_zone'])
            return loadZones
        except:
            return None
        
    def safe_url_insertions(self, email, url):
        """
        check weather url is already added or not
        """
        try:
            query = f"Select * from trueprice.save_graphview where url='{url}' AND user_id = (select id from trueprice.users where email='{email}');"
            result = self.engine.execute(text(query))
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
    
    def save_graph_url(self, email, control_table, location, start_date, end_date,operating_day,history,cob,operatin_day_timestamps, status):
        """
        saves the graph the user id
        """
        try:
            
            query = f"Insert into trueprice.save_graphview_v2 \
            (user_id,control_table_data,loadzone_data,cob_data, history_data,startdate_data,enddate_data, operating_day_data, operating_day_timestamps_data, status) \
            Values ((select id from trueprice.users where email='{email}'), {tuple(control_table)}, {tuple(location)}, {tuple(cob)}, {tuple(history)}, {tuple(start_date)}, {tuple(end_date)}, {tuple(operating_day)}, {tuple(operatin_day_timestamps)}, '{status}');"
            query = text("""
                INSERT INTO trueprice.save_graphview_v2  
                (user_id, control_table_data, loadzone_data, cob_data, history_data, startdate_data, enddate_data, operating_day_data, operating_day_timestamps_data, status)   
                VALUES 
                ((SELECT id FROM trueprice.users WHERE email=:email), :control_table, :location, :cob, :history, :start_date, :end_date, :operating_day, :operatin_day_timestamps, :status)
            """)
            
            result = self.engine.execute(query, {
            'email': email,
            'control_table': control_table,
            'location': location,
            'cob': cob,
            'history': history,
            'start_date': start_date,
            'end_date': end_date,
            'operating_day': operating_day,
            'operatin_day_timestamps': operatin_day_timestamps,
            'status': status,
    })
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        

    def get_user_graphs(self, email):
        """
        saves the graph the user id
        """
        try:
            data = []
            query = f"SELECT * FROM trueprice.save_graphview_v2 WHERE user_id = ((select id from trueprice.users where email='{email}'));"
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"graph_id": row['graph_id'], "user_id": row['user_id'], "status": row['status']})
            return data
        except :
            return data
    
    def remove_graphview(self, graph_id):
        """
        removes the  graph from the user panel
        """

        try:
            query = f"DELETE FROM trueprice.save_graphview_v2 WHERE graph_id ={graph_id};"
            result = self.engine.execute(text(query))
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        
    def get_emails(self):
        """
        get all emails from system
        """
        data = []
        try:
            query = f"SELECT * FROM trueprice.users where privileged_level = 'admin';"
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append(row['email'])
            return data
        except :
            return data
        

    def share_graph(self, email, graph_id):
        """
        share graph with other users of the application
        """

        query = text(f"""
            INSERT INTO trueprice.save_graphview_v2  
            (user_id, control_table_data, loadzone_data, cob_data, history_data, startdate_data, enddate_data, operating_day_data, operating_day_timestamps_data, status)   
            SELECT 
                (SELECT id FROM trueprice.users WHERE email='{email}') AS user_id, 
                control_table_data, 
                loadzone_data, 
                cob_data, 
                history_data, 
                startdate_data, 
                enddate_data, 
                operating_day_data, 
                operating_day_timestamps_data, 
                'shared' AS status
            FROM trueprice.save_graphview_v2
            WHERE graph_id ={graph_id};
        """)
        try:
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        
    def get_graph_data(self, graph_id):
        """
        fetches the data from the database
        """

        query = f"""
            SELECT 
                user_id, 
                control_table_data, 
                loadzone_data, 
                cob_data, 
                history_data, 
                startdate_data, 
                enddate_data, 
                operating_day_data, 
                operating_day_timestamps_data, 
                status
            FROM trueprice.save_graphview_v2
            WHERE graph_id = {graph_id};
        """
        control_table_data = []
        location = []
        cob_data = []
        history_data = []
        startdate_data = []
        enddate_data = []
        operating_day_data = []
        operating_day_timestamps_data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                control_table_data = row['control_table_data']
                location = row['loadzone_data'] 
                cob_data = row['cob_data']
                history_data = row['history_data']
                startdate_data = row['startdate_data']
                enddate_data = row['enddate_data']
                operating_day_data = row['operating_day_data']
                operating_day_timestamps_data = row['operating_day_timestamps_data']
                status = row['status']

            return control_table_data, location, cob_data, history_data, startdate_data, enddate_data, operating_day_data, operating_day_timestamps_data 
        except :
            return control_table_data, location, cob_data, history_data, startdate_data, enddate_data, operating_day_data, operating_day_timestamps_data



