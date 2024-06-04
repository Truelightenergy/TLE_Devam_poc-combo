"""
handles the operation of the notification events
"""

import datetime
import pandas as pd
from flask import session
from .notifier_model import NotifierUtil
from ..extractors.helper.extraction_rules import Rules

class Util:
    """
    handles the operation of the notification events
    """
    def __init__(self):
        """
        setup files for notifications
        """

        self.db_util = NotifierUtil()
        self.filter = Rules()

    def notifications_item_calculations(self, latest_curve_data, prev_curve_data):
        """
        calculate difference between data for both increase and decrease volumes
        """
        data_items = []
        #only date part matters for month column
        latest_curve_data['month'] = pd.to_datetime(latest_curve_data['month'])
        prev_curve_data['month'] = pd.to_datetime(prev_curve_data['month'])

        latest_curve_data['month'] = latest_curve_data['month'].dt.date
        prev_curve_data['month'] = prev_curve_data['month'].dt.date
        
        merged_df = pd.merge(latest_curve_data, prev_curve_data, on=['month', 'control_area', 'state', 'load_zone', 'capacity_zone', 'utility', 'strip', 'cost_group', 'cost_component', 'sub_cost_component'], suffixes=('_latest', '_prev'))

        # Calculate increase and decrease data
        increase_df = merged_df[(merged_df['data_latest'] - merged_df['data_prev']) >= 2]
        decrease_df = merged_df[(merged_df['data_prev'] - merged_df['data_latest']) >= 2]

        # Process increase data
        for itr, row in increase_df.iterrows():
            location = f"{row['control_area']}, {row['load_zone']} ({row['strip']})"
            data = (row['data_latest'] - row['data_prev'])
            data_prct = round((abs(row['data_latest'] - row['data_prev']) / row['data_latest']) * 100, 2)
            date = row['month']
            data_items.append({"location": location, "data_shift": data, "data_shift_prct": data_prct, "date": date, "volume": "increase"})

        # Process decrease data
        for itr, row in decrease_df.iterrows():
            location = f"{row['control_area']}, {row['load_zone']} ({row['strip']})"
            data = (row['data_latest'] - row['data_prev'])
            data_prct = round((abs(row['data_prev'] - row['data_latest']) / row['data_prev']) * 100, 2)
            date = row['month']
            data_items.append({"location": location, "data_shift": data, "data_shift_prct": data_prct, "date": date, "volume": "decrease"})

        # If no significant data found, get the max data_prct change within the bounds
        if not data_items:
            merged_df = pd.merge(latest_curve_data, prev_curve_data, on=['month', 'control_area', 'state', 'load_zone', 'capacity_zone', 'utility', 'strip', 'cost_group', 'cost_component', 'sub_cost_component'], suffixes=('_latest', '_prev'))
            bound_df = merged_df[(merged_df['data_latest'] - merged_df['data_prev']).abs() < 2]
            if not bound_df.empty:
                bound_df['data_shift_prct'] = bound_df.apply(
                    lambda row: round((abs(row['data_latest'] - row['data_prev']) / (row['data_latest'] if (row['data_latest'] - row['data_prev']) >= 0 else row['data_prev'])) * 100, 2),
                    axis=1
                )
                max_row = bound_df.loc[bound_df['data_shift_prct'].idxmax()]
                location = f"{max_row['control_area']}, {max_row['load_zone']} ({max_row['strip']})"
                data = (max_row['data_latest'] - max_row['data_prev'])
                data_prct = max_row['data_shift_prct']
                date = max_row['month']
                volume = "increase" if (max_row['data_latest'] - max_row['data_prev']) >= 0 else "decrease"
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
        latest_curve_data = self.key_nodals(latest_curve_data, filename)
        prev_curve_data = self.key_nodals(prev_curve_data, filename)

        if (latest_curve_data is None) or (prev_curve_data is None):
            self.db_util.update_notification_status(curvestart, filename)
            return
                
        data = self.notifications_item_calculations(latest_curve_data, prev_curve_data)
        # update notificaions
        success_flag = self.db_util.queue_notifications(data)
        if success_flag:
            success_flag = self.db_util.update_notification_status(curvestart, filename)
            print(f"Notifciations add for upload {filename}_{curvestart}")
        else:
            print(f"Unable to add notifciations for upload {filename}_{curvestart}")

        return
    
    def key_nodals(self, dataframe, filename):
        """
        filters only key nodals point
        """
        
        if 'miso' in filename.lower():
            return None
        
        filters = []

        # for ercot
        if 'ercot' in filename.lower():
            filters = ['NORTH ZONE']
        # for nyiso
        elif 'nyiso' in filename.lower():
            filters = ['ZONE A', 'ZONE G', 'ZONE J']
        # for pjm
        elif 'pjm' in filename.lower():
            filters = ['AD HUB', 'WEST HUB', 'EAST HUB', 'NI HUB']
        # for isone
        elif 'isone' in filename.lower():
            filters = ['MASS HUB']
        

        if len(filters)>0:
            dataframe = dataframe[dataframe['load_zone'].isin(filters)]
        return dataframe

    def setup_notifications(self):
        """
        setup the notifications after calculations
        """
        results = self.db_util.get_noifications_events()
        for row in results:
            self.calculate_price_change(row['curvestart'], row['filename'])
        return None
    
    def filter_data(self, dataframe, rules):
        """
        filter data based on the rules
        """

        dataframes = []
        dataframe["control_table"] = dataframe["location"].apply(lambda x: x.split(',')[0].split('in')[-1].strip().lower()+"_energy")
        dataframe["load_zone"] = dataframe["location"].apply(lambda x: x.split(',')[1].split('(5x16)')[0].strip())
        dataframe['strip'] = '5x16'

        for row in rules:
            query = f"control_table == '{row['control_table']}' & load_zone == '{row['load_zone']}' & strip == '{row['strip']}'"
            df = dataframe.query(query)
            dataframes.append(df)
        if len(dataframes)>=1:    
            return pd.concat(dataframes, axis=0), "success"
        return None, "error"          


    def fetch_todays_notifications(self):
        """
        extracts all latest notifications
        """

        notification_data = self.db_util.extract_latest_notifications()
        dataframe = pd.DataFrame(notification_data)
        email = session["user"]
        if session["level"]!= 'admin':
            rules = self.filter.fetch_module_rules("_energy", email)
            dataframe, status = self.filter_data(dataframe, rules)
            if status =='success':
                notification_data =  dataframe.to_dict(orient='records')



        notification_data = sorted(notification_data, key=lambda x: x['price_shift_prct'],  reverse=True)[:9]
        # processed_notifications = []
        # for notification in notification_data:
        #     if notification['price_shift'] == 'increase':
        #         weigh = 'gain'
        #     else:
        #         weigh = 'loss'
        #     val = "{:.5f}".format(notification['price_shift_value'])
        #     processed_notifications.append(f"The prompt month energy in {notification['location']} has {notification['price_shift']} by ${val}($/kWh) resulting in a {round(notification['price_shift_prct'], 2)}% {weigh}.")


        return notification_data
    
    def get_all_uploads(self):
        """
        fetch latest curvestart from the ingestion
        """
        return self.db_util.get_all_uploads()
    
    def fetch_latest_time_stamp(self):
        """
        fetch latest curvestart from the ingestion
        """
        return self.db_util.fetch_latest_curve_date()
    
    def curves_catalog(self):
        """
        Get catalog data for monthly normalized data used for curves.
        """
        return self.db_util.curves_catalog()