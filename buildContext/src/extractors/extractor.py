"""
makes query to the database and returns to the database
"""

import pandas as pd
from flask import session
from .extraction_rules import Rules
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
        self.filter = Rules()

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
            
            control_table = f"{query_strings['iso']}_{query_strings['curve_type']}"
            email = session["user"]
            if session["level"]!= 'admin':
                rules = self.filter.filter_data(control_table, email)
                dataframe, status = self.dataframe_filtering(dataframe, rules)
            
                if status != "success":
                    return None, "No Subscription available"

            if download_type=="csv":
                dataframe = self.post_processing_csv(dataframe, query_strings["curve_type"]) 
            else:
                dataframe = self.post_processing_json(dataframe)
                
            return dataframe, status
        except:
            return None, "Unable to Fetch Data"

    def dataframe_filtering(self, dataframe, rules):
        """
        filter the data based on the user subscription rules
        """
        dataframes = []
        for row in rules:
            query = f"control_area == '{row['control_area']}' & state == '{row['state']}' & load_zone == '{row['load_zone']}' & capacity_zone == '{row['capacity_zone']}' & utility == '{row['utility']}' & strip == '{row['strip']}' & cost_group == '{row['cost_group']}' & cost_component == '{row['cost_component']}' & sub_cost_component == '{row['sub_cost_component']}'"
            df = dataframe.query(query)
            df = df.loc[(df['month'] >= row['startmonth']) & (df['month'] <= row['endmonth'])]
            dataframes.append(df)
        if len(dataframes)>=1:    
            return pd.concat(dataframes, axis=0), "success"
        return None, "error"
        


