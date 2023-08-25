import croniter
import datetime
from .notifier_model import NotifierUtil
from .emailer import Email


class Process_Notifier:

    def __init__(self):
        self.db_util = NotifierUtil()
        self.email_sender = Email()

    
    
    def setup_next_schdule(self, notifier_id, cron_pattern):
        """
        setup the next schedule for the sending notifications
        """
        return self.db_util.schedule_next_notification(notifier_id, cron_pattern)

    def fetch_users_email(self, user_id):
        """extract the email of the user based on its id"""
        return self.db_util.get_user_email(user_id)
    
    def send_notificaions(self, data):
        """
        this method is reponsible for sending the notification to each users
        """
        notification_id = data["notification_id"]
        users = data["user_id"]
        head = data["subject_content"]
        body = data["body_content"]
        body = body.format(username = "User", location = data["location"], price_shift = data["price_shift"], price_shift_value= "$"+str(round(data["price_shift_value"], 2)), price_shift_prct = str(round( data["price_shift_prct"],2))+"%")

        emails= self.fetch_users_email(users)
        for email in emails:
            self.email_sender.send_email(head, body, email)

        self.db_util.log_notification(emails, notification_id, head)

        return True
    
   
    def process_notification(self):
        """
        check only those notifications whcih are met and process them
        """

        try:
            results = self.db_util.fetch_pending_notifications()
            success_flag = False
            for row in results:
                success_flag = self.send_notificaions(row)
                if success_flag:
                    success_flag = self.setup_next_schdule(row["notification_id"], row['cron_pattern'])
                    self. db_util.update_status(row["change_id"], "processed")
                else:
                    self. db_util.update_retries(row["change_id"], row["retries"]+1)
            if success_flag:
                print("Pending Notifications are done")
            else:
                print("No Notifications Pending")
                

        except:
            print("Something went Wrong while sending the notifications")



