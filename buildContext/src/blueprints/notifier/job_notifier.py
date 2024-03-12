import croniter
import datetime
from .notifier_model import NotifierUtil
from .emailer import Email
from ..extractors.helper.extraction_rules import Rules


class Process_Notifier:

    def __init__(self):
        self.db_util = NotifierUtil()
        self.email_sender = Email()
        self.filter = Rules()

    
    
    def setup_next_schdule(self, notifier_id, cron_pattern):
        """
        setup the next schedule for the sending notifications
        """
        return self.db_util.schedule_next_notification(notifier_id, cron_pattern)

    def fetch_users_email(self, user_id):
        """extract the email of the user based on its id"""
        return self.db_util.get_user_email(user_id)
    
    def valid_authorization(self, rules, control_table, load_zone, strip):
        """
        validate access to the notifications
        """
        flag = False
        for row in rules:
            if(row['control_table']==control_table) and (row['load_zone']==load_zone) and (row['strip']== strip):
                flag = True
                break
        return flag
    
    def send_notificaions(self, data):
        """
        this method is reponsible for sending the notification to each users
        """
        notification_id = data["notification_id"]
        users = data["user_id"]
        head = data["subject_content"]
        body = data["body_content"]

        header_sec, body_sec, tail_sec = body.split("<br/><br/>")
        notifications = body_sec.split("<br/>")
        
        emails= self.fetch_users_email(users)
        for email in emails:
            is_admin = self.filter.check_admin_privileges(email)
            custom_notification_body = ""
            for notif in notifications:
                rules = self.filter.fetch_module_rules("_energy", email)
                control_table = notif.split(',')[0].split('in')[-1].strip().lower()+"_energy"
                load_zone = notif.split(',')[1].split('(5x16)')[0].strip()
                strip = '5x16'

                if (is_admin) or (self.valid_authorization(rules, control_table, load_zone, strip)):
                    custom_notification_body = f"{custom_notification_body}<br />{notif}<br />"

            custom_notification_body = f"{header_sec}<br/>{custom_notification_body}<br/>{tail_sec}"
            self.email_sender.send_email(head, custom_notification_body, email)

        for not_id in notification_id:
            self.db_util.log_notification(emails, not_id, head)

        return True
    
   
    def process_notification(self):
        """
        check only those notifications whcih are met and process them
        """

        try:
            results = self.db_util.fetch_pending_notifications()
            # Use a set to store unique locations and a dictionary comprehension to filter unique dicts
            unique_locations = set()
            results = [unique_locations.add(d['location']) or d for d in results if d['location'] not in unique_locations]
            results = results[:9]
            results = sorted(results, key=lambda x: x['price_shift_prct'],  reverse=True)
            data = {
                "notification_id" : list(),
                "body_content": ""
            }
            for i, row in enumerate(results):
                if row["price_shift"] == "increase":
                    gl = "gain"
                else:
                    gl = "loss"

                notification_id = row["notification_id"]
                user = row["user_id"]
                head = row["subject_content"]
                body = row["body_content"]
                body = body.format(username = "User", 
                                   location = row["location"], 
                                   price_shift = row["price_shift"], 
                                   price_shift_value= "$"+str(round(row["price_shift_value"], 2)), 
                                   price_shift_prct = str(round( row["price_shift_prct"],2))+"%",
                                   gl = gl)
                header_body, body_content, tail_body = body.split("<br/>")

                data['user_id'] = user
                data['subject_content'] = head
                data['body_content'] = f"{data['body_content']}<br/>{body_content}"
                data['notification_id'].append(notification_id)
                if i == (len(results)-1):
                    data['body_content'] = f"{header_body}<br/>{data['body_content']}<br/><br/>{tail_body}"

            success_flag = self.send_notificaions(data)
            if success_flag:
                # success_flag = self.setup_next_schdule(row["notification_id"], row['cron_pattern'])
                self. db_util.update_status(row["event_id"], "processed")
            else:
                self. db_util.update_retries(row["event_id"], row["retries"]+1)
            if success_flag:
                print("Pending Notifications are done")
            else:
                print("No Notifications Pending")
                

        except:
            print("Something went Wrong while sending the notifications")



