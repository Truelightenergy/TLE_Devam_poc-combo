"""
handles the operation of the headrooms calculations
"""

import plotly
import json
import pandas as pd
import plotly.io as pio
import plotly.express as px

import datetime
import numpy as np
from .headroom_model import HeadroomModel
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

    def get_headroom_heatmap(self):
        """
        fetches latest headroom heatmap data from the database
        """
        data = self.headroom_model.get_headrooms_data()
        return data

    def calculate_headrooms(self):
        """
        calculates the headrooms prices
        """
        try: 
            data = self.headroom_model.get_waiting_headrooms()
            for instance in data:
                control_areas = ['nyiso', 'pjm', 'ercot', 'miso', 'isone']
                filename = next((region for region in control_areas if region in instance['filename']), None)
                matrix_data = self.headroom_model.get_matrix_data(instance['curvestart'], filename)
                ptc_data = self.headroom_model.get_ptc_data(filename)

                # converting data to the dataframes
                ptc_df = pd.DataFrame(ptc_data)
                # ptc_df = ptc_df.drop(columns=['lookup_id']) 

                
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
                df['headroom_prct'] = df['headroom_prct'].replace(-np.inf, -0.999)
                df['curvestart'] = instance['curvestart']


                df = df.drop([col for col in df.columns if '_y' in col], axis=1)
                df.columns = [col.split('_x')[0] if '_x' in col else col for col in df.columns]

                

                # ingest calculated values
                if self.headroom_model.headroom_ingestion(df):
                    self.headroom_model.mark_headroom_done(instance['curvestart'],instance['filename'])
                    print("*** Headroom Ingestion Successful ***")
                else:
                    print("*** Headroom Ingestion Failed ***")
        except:
            print("*** Headroom Ingestion Failed ***")
    
