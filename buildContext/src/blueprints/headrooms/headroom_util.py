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

class Util:
    """
    handles the operation of the headrooms calculations
    """
    def __init__(self):
        """
        setup files for headrooms
        """
        secret_key = "super-scret-key"
        secret_salt = "secret-salt"
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
                matrix_data = self.headroom_model.get_matrix_data(instance['curvestart'])
                ptc_data = self.headroom_model.get_ptc_data()

                # converting data to the dataframes
                matrix_df = pd.DataFrame(matrix_data)
                ptc_df = pd.DataFrame(ptc_data)

                # convert MWH to KWH in matrix df
                matrix_df['total_bundled_price'] = matrix_df['total_bundled_price'] / 1000
                ptc_df['data'] = ptc_df['data'].astype(float)
                matrix_df['total_bundled_price'] = matrix_df['total_bundled_price'].astype(float)

                # merging ptc and matrix dataframe on common characteristics

                common_columns = ['control_area_type', 'control_area', 'state', 'load_zone',
                                    'capacity_zone', 'utility', 'strip', 'cost_group', 'cost_component', 'load_profile']
                
                df = pd.merge(matrix_df, ptc_df, on=common_columns, how='inner')
                df = df.rename(columns={'data': 'ptc'})
                df['headroom'] = df['ptc'] - df['total_bundled_price']
                df['headroom_prct'] = (df['headroom'] / df['ptc'])*100
                df['headroom_prct'] = df['headroom_prct'].replace(-np.inf, -0.999)
                df['curvestart'] = instance['curvestart']
                

                # ingest calculated values
                if self.headroom_model.headroom_ingestion(df):
                    self.headroom_model.mark_headroom_done(instance['curvestart'],instance['filename'])
                    print("*** Headroom Ingestion Successful ***")
                else:
                    print("*** Headroom Ingestion Failed ***")
        except:
            print("*** Headroom Ingestion Failed ***")
    
