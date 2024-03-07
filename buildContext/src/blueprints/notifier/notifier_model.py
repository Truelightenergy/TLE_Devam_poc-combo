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
            query = f"""SELECT
                            *
                        FROM trueprice.languages AS lg
                        JOIN trueprice.email_templates AS et ON lg.language_code = 'en' -- Replace 'en' with the appropriate language code
                        JOIN trueprice.email_template_contents AS etc ON et.template_id = etc.template_id AND lg.language_id = etc.language_id
                        JOIN trueprice.notification_events AS ne ON ne.event_name <> '' 
                        JOIN trueprice.price_changes_notifications as pcg ON pcg.event_id= ne.event_id AND pcg.status='waiting' AND pcg.retries<5
                        JOIN trueprice.notifications AS ntf ON ntf.event_id = ne.event_id AND ntf.template_id = et.template_id
                        JOIN trueprice.schedule_patterns as sch ON ntf.notification_id = sch.notification_id AND sch.next_notification_time <= '{datetime.datetime.now()}';
                        
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
        query = """select * from trueprice.price_change_trigger where status = 'waiting' and filename  like '%%_energy';"""
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
            base_query = "INSERT INTO trueprice.price_changes_notifications (price_shift_value, price_shift_prct, price_shift, location, curvestart, event_id) VALUES"
            values = []
            for query_strings in data_items:
                value_set = f"('{query_strings['data_shift']}', '{query_strings['data_shift_prct']}', '{query_strings['volume']}', '{query_strings['location']}', '{query_strings['date']}', (select event_id from trueprice.notification_events where event_name ='PRICE_CHANGE'))"
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

        query = """
                SELECT DISTINCT ON (location) change_id, price_shift_value, price_shift_prct, price_shift, location
                FROM (                                        
                    SELECT change_id, price_shift_value, price_shift_prct, price_shift, location
                    FROM trueprice.price_changes_notifications
                    ORDER BY change_id DESC
                ) AS bottom_9
                ORDER BY location, change_id DESC;
                """
        data = []
        try:
            results = self.engine.execute(query).fetchall()
            for row in results:
                data.append({"price_shift_value": row['price_shift_value'], "price_shift_prct": row['price_shift_prct'],
                             "price_shift": row['price_shift'], "location": row['location']
                             })

            return data
        except:
            return data
        
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





        
    