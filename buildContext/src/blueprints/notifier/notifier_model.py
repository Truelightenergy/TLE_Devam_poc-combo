"""
handles all the database operations for the notifier
"""

import croniter
import pandas as pd
import datetime
from sqlalchemy import text
from utils.database_connection import ConnectDatabase

class NotifierUtil:

    def __init__(self):
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def calculate_next_notifications_time(self, cron_patterns):
        """
        calculate the next time stamp for notification based on the cron patterns
        """
        now = datetime.datetime.now()
        cron = croniter.croniter(cron_patterns, now)
        nextdatetime = cron.get_next(datetime.datetime)
        return nextdatetime

    def schedule_next_notification(self, notifier_id, cron_pattern):
        """
        setup the next schedule for the sending notifications
        """
        next_time = self.calculate_next_notifications_time(cron_pattern)
        query = f"update trueprice.schedule_patterns set next_notification_time = '{next_time}' WHERE notification_id ={notifier_id};"
        try:
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def get_user_email(self, user_id):

        """extract the email of the user based on its id"""

        try:
            emails = []
            if user_id:
                query = f"select * from trueprice.users WHERE id={user_id};"
            else:
                query = f"select * from trueprice.users;"
            result = self.engine.execute(query)
            for row in result:
                emails.append(row["email"])
            return emails
        except:
            return []
        
    def log_notification(self, user_emails, notification_id, msg):

        """
        log the notification in to the database
        """
        try:
            for email in user_emails:
                query = f"INSERT INTO trueprice.notifications_log(notification_id, user_id, message) VALUES ({notification_id}, (SELECT id FROM trueprice.users WHERE email='{email}'), '{msg}');"
                result = self.engine.execute(query)
                if result.rowcount > 0:
                    print(f"Notification Logged for user: {email}")
        except:
            print("something went wrong while logging notification")


    def fetch_pending_notifications(self):
        """
        check only those notifications whcih are met and process them
        """
        data = []
        try:
            # get notifications for prompt month only
            query = f"""SELECT *
                        FROM trueprice.languages AS lg
                        JOIN trueprice.email_templates AS et ON lg.language_code = 'en' -- Replace 'en' with the appropriate language code
                        JOIN trueprice.email_template_contents AS etc ON et.template_id = etc.template_id AND lg.language_id = etc.language_id
                        JOIN trueprice.notification_events AS ne ON ne.event_name <> '' 
                        JOIN trueprice.price_changes_notifications as pcg ON pcg.event_id= ne.event_id AND pcg.status='waiting' AND pcg.retries<5
                        JOIN trueprice.notifications AS ntf ON ntf.event_id = ne.event_id AND ntf.template_id = et.template_id
                        JOIN trueprice.schedule_patterns as sch ON ntf.notification_id = sch.notification_id AND sch.next_notification_time <= '{datetime.datetime.now()}'
                        where pcg.curvestart::date = (date_trunc('month', CURRENT_DATE) + interval '1 month')::date and pcg.change_within_bounds = false and pcg.notification_date::DATE = CURRENT_DATE AND pcg.status='waiting' AND pcg.retries<5;
                        """
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"notification_id": row["notification_id"], "user_id": row["user_id"], "subject_content" :row["subject_content"], "body_content": row["body_content"], "cron_pattern": row["cron_pattern"], 
                             "event_id": row["event_id"], "price_shift": row["price_shift"], "price_shift_value": row["price_shift_value"], "price_shift_prct": row["price_shift_prct"], "location": row["location"], "curvestart": row["curvestart"], "status": row["status"], "retries": ["retries"]
                             })

            return data
        except:
            return data
        
    def get_noifications_events(self):
        """
        fetch the notification events which are pending 
        """
        #currently we only send notifications for price change for 9 key nodal points from energy curve
        query = """select * from trueprice.price_change_trigger where status = 'waiting' and filename  like '%%_energy' and curvestart ::DATE = current_date::DATE;"""
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"curvestart": row['curvestart'], "filename": row['filename']})

            return data
        except Exception as error:
            print(error)
            return data
        
    def get_cuves_data(self, cuvestart, filename):
        """
        extract the lates two curves data
        """
        latest_curve_data = self.get_single_curve_data(cuvestart, filename)
        prev_date = self.get_previous_date(cuvestart, filename)
        prev_curve_data = self.get_single_curve_data(prev_date, filename)
        return latest_curve_data, prev_curve_data

    def get_single_curve_data(self, curvestart, filename):
        """
        fetch the data from the single energy curve
        """

        try:
            query = f"select * from trueprice.{filename} where curvestart ='{curvestart}';"
            data_frame = pd.read_sql_query(sql=query, con=self.engine.connect())
            query = f"strip == '5x16'"
            # data_frame= data_frame[(data_frame['month'].dt.month == curvestart.month) & (data_frame['month'].dt.year == curvestart.year)]
            data_frame = data_frame.query(query)
            return data_frame
        except:
            return None
        
    def get_previous_date(self, curvestart, filename):
        """
        fetches the most recent data from the file
        """
        date = curvestart.date()
        previous_date = None
        try:
            query =f"""
                    SELECT MAX(curvestart) AS most_recent_date
                    FROM trueprice.{filename}
                    WHERE curvestart < '{date}';
                    """
            result = self.engine.execute(query)
            
            for row in result:
                previous_date = row['most_recent_date']
                break
            return previous_date
        except:
            return previous_date
        
    def update_notification_status (self, curvestart, filename):
        """
        update the status of the notifications
        """

        try : 
            query =f"update trueprice.price_change_trigger set status = 'processed' where status = 'waiting' and filename='{filename}' and curvestart = '{curvestart}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def queue_notifications(self, data_items):

        """
        setup the queue for notifications to be sent
        """
        try:
            base_query = "INSERT INTO trueprice.price_changes_notifications (price_shift_value, price_shift_prct, price_shift, location, curvestart,change_within_bounds,event_id) VALUES"
            values = []
            for query_strings in data_items:
                value_set = f"('{query_strings['data_shift']}', '{query_strings['data_shift_prct']}', '{query_strings['volume']}', '{query_strings['location']}', '{query_strings['date']}',{'TRUE' if query_strings['data_shift'] < 2 else 'FALSE'}, (select event_id from trueprice.notification_events where event_name ='PRICE_CHANGE'))"
                values.append(value_set)
            
            query = base_query + ", ".join(values)
            query = text(query)
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def update_status(self, event_id, status):
        """
        update the status of the notifications
        """


        # Get the current date
        current_date = datetime.datetime.now().date()

        # Create a new datetime object with time set to 00:00:00
        todays_date = datetime.datetime.combine(current_date, datetime.time(0, 0, 0))


        query = f"update trueprice.price_changes_notifications set status ='{status}', notification_date='{todays_date}'  where event_id = {event_id} and status='waiting'; "
        try:
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def update_retries(self, change_id, retries):
        """
        update the retries count of the notifications
        """
        query = f"update trueprice.price_changes_notifications set retries ='{retries}' where change_id = {change_id};"
        try:
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def extract_latest_notifications(self):
        """
        extracts all latest notifications
        """
        #Get notifications for prompt month only
        query = """
                 SELECT DISTINCT ON (location) change_id, price_shift_value, price_shift_prct, price_shift, location
                    FROM (                                        
                        SELECT  change_id, price_shift_value, price_shift_prct, price_shift, location 
                        FROM trueprice.price_changes_notifications
                        where  
                        	curvestart::date = (date_trunc('month', CURRENT_DATE) + interval '1 month')::date 
                        and 
                        		(created_on::DATE = CURRENT_DATE::DATE)
                        ORDER BY price_shift_prct desc, notification_date desc
                    ) AS bottom_9
                    ORDER BY location DESC;
                """
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                if not (any(sub in row['location'].lower() for sub in ['ercot, north zone', 'nyiso, zone a', 'nyiso, zone g', 'nyiso, zone j', 'pjm, ad hub', 'pjm, west hub', 'pjm, east hub', 'pjm, ni hub', 'isone, mass hub'])) or 'Control Area: ' in row['location']:
                    continue
                data.append({"price_shift_value": row['price_shift_value'], "price_shift_prct": row['price_shift_prct'],
                             "price_shift": row['price_shift'], "location": row['location']
                             })

            return data
        except:
            return data
        
    def get_all_uploads(self):
        """
        extracts all uploads
        """

        query = """
               SELECT 
                    UPPER(split_part(filename, '_', 1)) AS "File Type",
                    UPPER(REPLACE(filename, '_cob', '')) AS "File Name",
                    CASE
                        WHEN POSITION('COB' IN filename) > 0 THEN 'Y'
                        ELSE 'N'
                    END AS "COB(Y/N)"
                FROM 
                    trueprice.uploads u	
                ORDER BY 
                    "File Type", "File Name";
                """
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"File Name": row['File Type'], 
                             "ISO": row['File Name'].split('_')[1],
                             "Operating Day": row['File Name'].split('_')[2],
                             "Time Stamp": row['File Name'].split('_')[3].split('.')[0],
                             "File Extension": row['File Name'].split('.')[-1],
                             "COB(Y/N)": row['COB(Y/N)']
                             })

            return data
        except:
            return data
    
    def get_all_heirarchies(self):
        """
        extract all the unique hierarchies by curve type
        """
        sql_queries = {
            'Energy': """
                SELECT DISTINCT 'Energy' AS "DataType", '' AS "Lookup ID1",control_area AS "Control Area", 
                                state AS "State", 
                                load_zone AS "Load Zone", 
                                capacity_zone AS "Capacity Zone", 
                                utility AS "Utility", 
                                strip AS "Block Type", 
                                cost_group AS "Cost Group", 
                                cost_component AS "Cost Component"
                FROM (
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.ercot_energy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.isone_energy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.nyiso_energy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.pjm_energy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.miso_energy
                ) AS t
                ORDER BY control_area;
            """,
            'Non-Energy': """
                SELECT DISTINCT 'Nonenergy' AS "DataType", '' AS "Lookup ID1",control_area AS "Control Area", 
                                state AS "State", 
                                load_zone AS "Load Zone", 
                                capacity_zone AS "Capacity Zone", 
                                utility AS "Utility", 
                                strip AS "Block Type", 
                                cost_group AS "Cost Group", 
                                replace( cost_component, ' ($/MWh)','') AS "Cost Component"
                FROM (
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.ercot_nonenergy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.isone_nonenergy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.nyiso_nonenergy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.pjm_nonenergy
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.miso_nonenergy
                ) AS t
                ORDER BY control_area;
            """,
            'Rec': """
                SELECT DISTINCT 'REC/RPS' AS "DataType", '' AS "Lookup ID1", control_area AS "Control Area", 
                                state AS "State", 
                                load_zone AS "Load Zone", 
                                capacity_zone AS "Capacity Zone", 
                                utility AS "Utility", 
                                strip AS "Block Type", 
                                cost_group AS "Cost Group", 
                                cost_component AS "Cost Component"
                FROM (
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.ercot_rec
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.isone_rec
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.nyiso_rec
                    UNION
                    SELECT control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component  
                    FROM trueprice.pjm_rec
                ) AS t
                ORDER BY control_area;
            """,
            'Line Loss': """
                SELECT DISTINCT * 
                FROM (
                    SELECT 'Line Loss' AS "DataType", '' AS "Lookup ID1", 
                            ca."name" AS "Control Area", 
                            s."name" AS "State", 
                            lz."name" AS "Load Zone", 
                            cz."name" AS "Capacity Zone", 
                            u."name" AS "Utility", 
                            bt."name" AS "Block Type", 
                            cg."name" AS "Cost Group", 
                            cc."name" AS "Cost Component"
                    FROM trueprice."hierarchy" h
                    INNER JOIN trueprice.curve_datatype cd ON cd.id = h.curve_datatype_id 
                    INNER JOIN trueprice.control_area ca ON ca.id = h.control_area_id 
                    INNER JOIN trueprice.state s ON s.id = h.state_id 
                    INNER JOIN trueprice.load_zone lz ON lz.id = h.load_zone_id 
                    INNER JOIN trueprice.capacity_zone cz ON cz.id = h.capacity_zone_id 
                    INNER JOIN trueprice.utility u ON u.id = h.utility_id 
                    INNER JOIN trueprice.block_type bt ON bt.id = h.block_type_id 
                    INNER JOIN trueprice.cost_group cg ON cg.id = h.cost_group_id 
                    INNER JOIN trueprice.cost_component cc ON cc.id = h.cost_component_id 
                    WHERE cd."name" = 'lineloss'
                ) AS t
                ORDER BY "Control Area";
            """,
            'Shaping': """
                SELECT DISTINCT * 
                FROM (
                    SELECT 'Shaping' AS "DataType", '' AS "Lookup ID1", 
                            ca."name" AS "Control Area", 
                            s."name" AS "State", 
                            lz."name" AS "Load Zone", 
                            cz."name" AS "Capacity Zone", 
                            u."name" AS "Utility", 
                            bt."name" AS "Block Type", 
                            cg."name" AS "Cost Group", 
                            cc."name" AS "Cost Component"
                    FROM trueprice."hierarchy" h
                    INNER JOIN trueprice.curve_datatype cd ON cd.id = h.curve_datatype_id 
                    INNER JOIN trueprice.control_area ca ON ca.id = h.control_area_id 
                    INNER JOIN trueprice.state s ON s.id = h.state_id 
                    INNER JOIN trueprice.load_zone lz ON lz.id = h.load_zone_id 
                    INNER JOIN trueprice.capacity_zone cz ON cz.id = h.capacity_zone_id 
                    INNER JOIN trueprice.utility u ON u.id = h.utility_id 
                    INNER JOIN trueprice.block_type bt ON bt.id = h.block_type_id 
                    INNER JOIN trueprice.cost_group cg ON cg.id = h.cost_group_id 
                    INNER JOIN trueprice.cost_component cc ON cc.id = h.cost_component_id 
                    WHERE cd."name" = 'shaping'
                ) AS t
                ORDER BY "Control Area";
            """,
            'Load Profile': """
                SELECT DISTINCT * 
                FROM (
                    SELECT 'Load Profile' AS "DataType", '' AS "Lookup ID1", 
                            ca."name" AS "Control Area", 
                            s."name" AS "State", 
                            lz."name" AS "Load Zone", 
                            cz."name" AS "Capacity Zone", 
                            u."name" AS "Utility", 
                            bt."name" AS "Block Type", 
                            cg."name" AS "Cost Group", 
                            cc."name" AS "Cost Component"
                    FROM trueprice."hierarchy" h
                    INNER JOIN trueprice.curve_datatype cd ON cd.id = h.curve_datatype_id 
                    INNER JOIN trueprice.control_area ca ON ca.id = h.control_area_id 
                    INNER JOIN trueprice.state s ON s.id = h.state_id 
                    INNER JOIN trueprice.load_zone lz ON lz.id = h.load_zone_id 
                    INNER JOIN trueprice.capacity_zone cz ON cz.id = h.capacity_zone_id 
                    INNER JOIN trueprice.utility u ON u.id = h.utility_id 
                    INNER JOIN trueprice.block_type bt ON bt.id = h.block_type_id 
                    INNER JOIN trueprice.cost_group cg ON cg.id = h.cost_group_id 
                    INNER JOIN trueprice.cost_component cc ON cc.id = h.cost_component_id 
                    WHERE h.curve_datatype_id = 2
                ) AS t
                ORDER BY "Control Area";
            """,
            'VLR': """
                SELECT DISTINCT * 
                FROM (
                    SELECT 'VLR' AS "DataType", '' AS "Lookup ID1", 
                            ca."name" AS "Control Area", 
                            s."name" AS "State", 
                            lz."name" AS "Load Zone", 
                            cz."name" AS "Capacity Zone", 
                            u."name" AS "Utility", 
                            bt."name" AS "Block Type", 
                            cg."name" AS "Cost Group", 
                            cc."name" AS "Cost Component"
                    FROM trueprice."hierarchy" h
                    INNER JOIN trueprice.curve_datatype cd ON cd.id = h.curve_datatype_id 
                    INNER JOIN trueprice.control_area ca ON ca.id = h.control_area_id 
                    INNER JOIN trueprice.state s ON s.id = h.state_id 
                    INNER JOIN trueprice.load_zone lz ON lz.id = h.load_zone_id 
                    INNER JOIN trueprice.capacity_zone cz ON cz.id = h.capacity_zone_id 
                    INNER JOIN trueprice.utility u ON u.id = h.utility_id 
                    INNER JOIN trueprice.block_type bt ON bt.id = h.block_type_id 
                    INNER JOIN trueprice.cost_group cg ON cg.id = h.cost_group_id 
                    INNER JOIN trueprice.cost_component cc ON cc.id = h.cost_component_id 
                    WHERE h.curve_datatype_id = 4
                ) AS t
                ORDER BY "Control Area";
            """
        }
        try:
            # Fetch the data
            dataframes = []
            for sheet_name, query in sql_queries.items():
                df = self.engine.execute(query).fetchall()
                dataframes.append(df)
                
            # Define the corresponding sheet names
            sheet_names = list(sql_queries.keys())
            return dataframes, sheet_names
        except:
            return None
        
            
    def fetch_latest_curve_date(self):
        query = "select MAX(DISTINCT(curvestart)) as curvestart from trueprice.ercot_energy;"
        date = None
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                date = row['curvestart']
                break
            return date
        except:
            return date

    def curves_catalog(self):
        query = '''
                select * from trueprice.monthly_reference_data;
        '''
        try:

            df = pd.read_sql_query(query, self.engine)
            return df.to_csv(index=False)
        
        except Exception as e:
            print('Error:', str(e))

        return {}



        
    