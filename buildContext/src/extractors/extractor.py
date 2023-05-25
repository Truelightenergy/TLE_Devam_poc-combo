"""
makes query to the database and returns to the database
"""

import pandas as pd
from database_connection import ConnectDatabase
from .nonenergy import NonEnergy
from .energy import Energy
from .rec import Rec

class Extractor:
    """
    class which expects filters to get data from the db and return in pandas
    """
    def __init__(self):
        """
        database connection will be loaded here
        """

        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

        self.non_energy = NonEnergy()
        self.energy = Energy()
        self.rec= Rec()

    def post_processing_csv(self, df, type):
        """
        post process the dataframe
        """


        if type =="energy":
            pivoted_df = pd.pivot_table(df, values='data', index=['month', 'curvestart', 'curveend', 'cob'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'sub_cost_component'], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Start', 'curveend': 'Curve End', 'month': "Month" , 'cob': 'COB'})

            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", " "]
            
            # returning dataframe
            return flattened_df
        
        else:
            pivoted_df = pd.pivot_table(df, values='data', index=['month', 'curvestart', 'curveend'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'sub_cost_component'], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Start', 'curveend': 'Curve End', 'month': "Month"})

            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", " "]
            
            # returning dataframe
            return flattened_df
    
    def post_processing_json(self, df):
        """
        post process the dataframe
        """
        columns=["month",'curvestart', 'curveend', "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'sub_cost_component']
        df= df[columns]
        df.columns = ["Month",'Curve Start', 'Curve End', "Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", 'Sub Cost Component']
        return df


    def get_custom_data(self, query_strings, download_type):
        """
        extracts the data from the database based on the query strings
        """
        try:

            dataframe = None
            status = "Unable to Fetch Data"
            if query_strings["curve_type"] == "nonenergy":
                dataframe, status = self.non_energy.extraction(query_strings)
            elif query_strings["curve_type"] == "energy":
                dataframe, status = self.energy.extraction(query_strings)
            elif query_strings["curve_type"] == "rec":
                dataframe, status = self.rec.extraction(query_strings)

            if not isinstance(dataframe, pd.DataFrame):
                    return dataframe, status

            if download_type=="csv":
                dataframe = self.post_processing_csv(dataframe, query_strings["curve_type"]) 
            else:
                dataframe = self.post_processing_json(dataframe)
                
            return dataframe, status
        except:
            return None, "Unable to Fetch Data"

            # http://127.0.0.1:5555/get_data?start=20230101&end=20230102&iso=isone&strip=24x7&curve_type=ancillarydata&type=csv
            # http://127.0.0.1:5555/get_data?start=20230101&end=20230109&iso=isone&strip=7x8&curve_type=forwardcurve&type=csv
        

