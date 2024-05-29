"""
handles the operation of the headrooms calculations
"""

import plotly
import json
import pandas as pd
import plotly.io as pio
import plotly.express as px
import pytz
from flask import session
import datetime
import numpy as np
from .headroom_model import HeadroomModel
from ..extractors.helper.extraction_rules import Rules
from utils.configs import read_config

config = read_config()
class Util:
    """
    handles the operation of the headrooms calculations
    """
    def __init__(self):
        """
        setup files for headrooms
        """
        secret_key = config['secret_key']
        secret_salt = config['secret_salt']
        self.headroom_model = HeadroomModel(secret_key, secret_salt)
        self.filter = Rules()
        

    def dataframe_filtering(self, dataframe, rules, control_table):
        """
        filter the data based on the user subscription rules
        """
        dataframes = []
        for row in rules:
            if ("headroom" in control_table) or ("ptc" in control_table):
                query = f"control_area == '{row['control_area']}' & state == '{row['state']}' & load_zone == '{row['load_zone']}' & capacity_zone == '{row['capacity_zone']}' & utility == '{row['utility']}' & strip == '{row['strip']}' & cost_group == '{row['cost_group']}' & cost_component == '{row['cost_component']}'"
            else:
                query = f"control_area == '{row['control_area']}' & state == '{row['state']}' & load_zone == '{row['load_zone']}' & capacity_zone == '{row['capacity_zone']}' & utility == '{row['utility']}' & strip == '{row['strip']}' & cost_group == '{row['cost_group']}' & cost_component == '{row['cost_component']}' & sub_cost_component == '{row['sub_cost_component']}'"
            df = dataframe.query(query)
            if (("headroom" in control_table) or ("ptc" in control_table) or ("matrix" in control_table)):
                pass
            else: 
                if row['balanced_month_range'] ==  0:
                    df = df.loc[(df['month'] >= row['startmonth']) & (df['month'] <= row['endmonth'])]
                else:
                    start_month, end_month = self.calculate_balanced_month(row['balanced_month_range'])
                    df = df.loc[(df['month'] >= start_month) & (df['month'] <= end_month)]
            dataframes.append(df)
        if len(dataframes)>=1:    
            return pd.concat(dataframes, axis=0), "success"
        return None, "error"
    
    def column_filter(self, dataframe):
        """
        filters specific columns
        """
        if (dataframe is not None) and len(dataframe) != 0 :
            dataframe =  dataframe[['state', 'utility', 'load_zone', 'utility_price', 'retail_price', 'headroom', 
                                    'headroom_prct', 'customer_type', 'term']]
        else:
            dataframe = pd.DataFrame()
        return dataframe

    def get_headroom_heatmap(self):
        """
        fetches latest headroom heatmap data from the database
        """
        data = self.headroom_model.get_headrooms_data()
        dataframe = pd.DataFrame(data)
        email = session["user"]
        if session["level"]!= 'admin':
            rules = self.filter.fetch_module_rules("headroom", email)
            dataframe, status = self.dataframe_filtering(dataframe, rules, "headroom")
        dataframe =  self.column_filter(dataframe)
        data = dataframe.to_dict(orient='records')

        return data

    def calculate_headrooms(self):
        """
        calculates the headrooms prices
        """
        try: 
            data = self.headroom_model.get_waiting_headrooms()
            for instance in data:
                control_areas = ['nyiso', 'pjm', 'ercot', 'miso', 'isone']
                filename = next((region for region in control_areas if region in instance['filename'].lower()), None)
            
                try:
                   
                    matrix_data = self.headroom_model.get_matrix_data(instance['curvestart'], filename)
                    ptc_data = self.headroom_model.get_ptc_data(filename,instance['curvestart'])

                    # converting data to the dataframes
                    ptc_df = pd.DataFrame(ptc_data)
                    # ptc_df = ptc_df.drop(columns=['lookup_id']) 


                    matrix_df = pd.DataFrame(matrix_data)
                    # matrix_df = matrix_df.drop(columns=['matching_id'])

                    current_ptc_date = ptc_df['curvestart'].unique()[0]

                    current_ptc_date = current_ptc_date.replace(day=1)
                    # Set the time stamps to 0
                    # current_ptc_date = current_ptc_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    # ptc_df = ptc_df[ptc_df['month'].dt.date == current_ptc_date.date]
                    ptc_df = ptc_df[
                        (ptc_df['month'].dt.year == current_ptc_date.year) &
                        (ptc_df['month'].dt.month == current_ptc_date.month) &
                        (ptc_df['month'].dt.day == current_ptc_date.day)
                    ]


                    matrix_df = pd.DataFrame(matrix_data)
                    # matrix_df = matrix_df.drop(columns=['matching_id'])

                    # convert MWH to KWH in matrix df
                    matrix_df['total_bundled_price'] = matrix_df['total_bundled_price'] / 1000
                    ptc_df['data'] = ptc_df['data'].astype(float)
                    matrix_df['total_bundled_price'] = matrix_df['total_bundled_price'].astype(float)


                    # merging ptc and matrix dataframe on common characteristics
                    df = pd.merge(matrix_df, ptc_df, left_on='lookup_id', right_on='matching_id', how='inner')

                    df = df.rename(columns={'data': 'ptc'})
                    df['headroom'] = df['ptc'] - df['total_bundled_price']
                    df['headroom_prct'] = (df['headroom'] / df['ptc'])*100
                    df['headroom_prct'] = df['headroom_prct'].replace(-np.inf, 0)
                    df['curvestart'] = instance['curvestart']


                    df = df.drop([col for col in df.columns if '_y' in col], axis=1)
                    df.columns = [col.split('_x')[0] if '_x' in col else col for col in df.columns]



                    # ingest calculated values
                    if self.headroom_model.headroom_ingestion(df):
                        self.headroom_model.mark_headroom_done(instance['curvestart'],instance['filename'])
                        print("*** Headroom Ingestion Successful ***",filename)
                    else:
                        print("*** Headroom Ingestion Failed ***",filename)
                except Exception as e:
                    print(e)
                    print("*** Headroom Ingestion Failed ***",filename)
        except:
            print("*** Headroom Ingestion Failed ***")
    
