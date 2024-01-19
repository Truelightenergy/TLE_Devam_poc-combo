"""
handles the operation of the notification events
"""

import datetime
import pandas as pd
from .notifier_model import NotifierUtil

class Util:
    """
    handles the operation of the notification events
    """
    def __init__(self):
        """
        setup files for notifications
        """

        self.db_util = NotifierUtil()

    def notifications_item_calculations(self, latest_curve_data, prev_curve_data, volume):
        """
        calculate difference between datas
        """
        data_items = []

        
        merged_df = pd.merge(latest_curve_data, prev_curve_data, on=['month', 'control_area', 'state', 'load_zone', 'capacity_zone', 'capacity_zone', 'utility', 'strip', 'cost_group', 'cost_component', 'sub_cost_component'], suffixes=('_latest', '_prev'))
        if volume == "increase":
            filtered_df = merged_df[(merged_df['data_latest'] - merged_df['data_prev']) >=2]
        else:
            filtered_df = merged_df[(merged_df['data_prev'] - merged_df['data_latest']) >=2]
        for itr, row in filtered_df.iterrows():
            location = f"{row['control_area']}, {row['load_zone']} ({row['strip']})"
            data = (row['data_latest'] - row['data_prev'])
            if volume == "increase":
                data_prct = round((abs(row['data_latest'] - row['data_prev'])/ row['data_latest'])*100, 2)
            else:
                data_prct = round((abs(row['data_prev'] - row['data_latest'])/ row['data_prev'])*100, 2)
            date = row['month']
            data_items.append({"location": location, "data_shift": data, "data_shift_prct": data_prct, "date": date, "volume": volume})

        return data_items
    

    def calculate_price_change(self, curvestart, filename):
        """
        calculates the price shift of single curve
        """

        latest_curve_data, prev_curve_data = self.db_util.get_cuves_data(curvestart, filename)
        if (latest_curve_data is None) or (prev_curve_data is None):
            self.db_util.update_notification_status(curvestart, filename)
            return
        # increase volume
        increased_data = self.notifications_item_calculations(latest_curve_data, prev_curve_data, "increase")
        # decrease volume
        decreased_data = self.notifications_item_calculations(latest_curve_data, prev_curve_data, "decrease")
        data = [*increased_data, *decreased_data]
        # update notificaions
        success_flag = self.db_util.queue_notifications(data)
        if success_flag:
            success_flag = self.db_util.update_notification_status(curvestart, filename)
            print(f"Notifciations add for upload {filename}_{curvestart}")
        else:
            print(f"Unable to add notifciations for upload {filename}_{curvestart}")

        return

    def setup_notifications(self):
        """
        setup the notifications after calculations
        """
        results = self.db_util.get_noifications_events()
        for row in results:
            self.calculate_price_change(row['curvestart'], row['filename'])
        return None
    
    def fetch_todays_notifications(self):
        """
        extracts all latest notifications
        """

        notification_data = self.db_util.extract_latest_notifications()
        notification_data = sorted(notification_data, key=lambda x: x['price_shift_prct'],  reverse=True)[:9]
        processed_notifications = []
        for notification in notification_data:
            processed_notifications.append(f"Energy in {notification['location']} has {notification['price_shift']} by ${round(notification['price_shift_value'], 2)} resulting in a {round(notification['price_shift_prct'], 2)}% gain.")


        return processed_notifications
    
    def fetch_latest_time_stamp(self):
        """
        fetch latest curvestart from the ingestion
        """
        return self.db_util.fetch_latest_curve_date()
