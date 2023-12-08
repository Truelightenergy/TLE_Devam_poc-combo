"""
makes query to the database and returns to the database
"""

import pandas as pd
from datetime import datetime, timedelta
from flask import session
from .helper.extraction_rules import Rules
from utils.database_connection import ConnectDatabase
from .helper.nonenergy import NonEnergy
from .helper.energy import Energy
from .helper.rec import Rec
from .helper.ptc import Ptc
from .helper.matrix import Matrix
from .helper.headroom import Headroom


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
        self.ptc = Ptc()
        self.matrix = Matrix()
        self.headroom = Headroom()
        self.filter = Rules()

    def post_processing_csv(self, df, type):
        """
        post process the dataframe
        """

        if type == 'headroom':
            pivoted_df = pd.pivot_table(df, values= ['headroom', 'headroom_prct'], index=['curvestart', 'month'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "control_area_type", "lookup_id2", "lookup_id3", "load_profile", "term"], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Update Date', 'month': "Curve Start Month"})

            # renaming columns
            flattened_df.columns.names =  ["Value", "Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Strip", "Cost Group", "Cost Component", "Control Area Type", "Lookup Id2", "Lookup Id3", "Load Profile", "Term"]

            # returning dataframe
            return flattened_df

        elif type=='matrix':
            df = df.drop(['id', 'curveend'], axis=1)
            return df.transpose()
            
        elif type == 'ptc':
            pivoted_df = pd.pivot_table(df, values='data', index=['curvestart', 'month'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "control_area_type", "lookup_id2", "lookup_id3","utility_name", "profile_load"], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Update Date', 'month': "Curve Start Month"})

            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", "lookup_id2", "lookup_id3", "Control_area_type", "Utility_name", "Profile_load"]

            # returning dataframe
            return flattened_df
        
        elif type =="energy":
            pivoted_df = pd.pivot_table(df, values='data', index=['curvestart', 'month', 'cob'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'sub_cost_component'], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Update Date', 'month': "Curve Start Month" , 'cob': 'COB'})

            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", " "]
            
            # returning dataframe
            return flattened_df
        
        else:
            pivoted_df = pd.pivot_table(df, values='data', index=['curvestart', 'month'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'sub_cost_component'], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Update Date', 'month': "Curve Start Month"})

            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", " "]
            
            # returning dataframe
            return flattened_df
        
    
    def post_processing_json(self, df):
        """
        post process the dataframe
        """
        columns=["month", 'data', 'curvestart', "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'sub_cost_component']
        df= df[columns]
        df = df.copy()
        if not df.empty:
            df["curvestart"] = df["curvestart"].dt.strftime('%Y-%m-%d %H:%M:%S')
            df["month"] = df["month"].dt.strftime('%Y-%m-%d %H:%M:%S')
            
        
        df.columns = ["Curve Start Month", 'Data', 'Curve Update Date', "Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", 'Sub Cost Component']
        return df


    def get_custom_data(self, query_strings, download_type):
        """
        extracts the data from the database based on the query strings
        """
        try:

            dataframe = None
            status = "Unable to Fetch Data"
            if str(query_strings["curve_type"]).lower() == "nonenergy":
                dataframe, status = self.non_energy.extraction(query_strings)
            elif str(query_strings["curve_type"]).lower() == "energy":
                dataframe, status = self.energy.extraction(query_strings)
            elif str(query_strings["curve_type"]).lower() == "rec":
                dataframe, status = self.rec.extraction(query_strings)
            elif str(query_strings["curve_type"]).lower() == "ptc":
                dataframe, status = self.ptc.extraction(query_strings) 
            elif str(query_strings["curve_type"]).lower() == "matrix":
                dataframe, status = self.matrix.extraction(query_strings) 
            elif str(query_strings["curve_type"]).lower() == "headroom":
                dataframe, status = self.headroom.extraction(query_strings) 

            if not isinstance(dataframe, pd.DataFrame):
                    return dataframe, status
            
            # for un conditional responses (no subscription hence all data return)
            un_conditional_curves = ['ptc', 'matrix', 'headroom']
            if str(query_strings["curve_type"]).lower() in un_conditional_curves:
                dataframe = self.post_processing_csv(dataframe, str(query_strings["curve_type"]).lower())
                return dataframe, status
            
            control_table = f"{query_strings['iso']}_{query_strings['curve_type']}"
            email = session["user"]
            if session["level"]!= 'admin':
                rules = self.filter.filter_data(control_table, email)
                dataframe, status = self.dataframe_filtering(dataframe, rules)
            
                if status != "success":
                    return None, "No Subscription available"

            if download_type.lower()=="csv":
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
            if row['balanced_month_range'] ==  0:
                df = df.loc[(df['month'] >= row['startmonth']) & (df['month'] <= row['endmonth'])]
            else:
                start_month, end_month = self.calculate_balanced_month(row['balanced_month_range'])
                df = df.loc[(df['month'] >= start_month) & (df['month'] <= end_month)]
            dataframes.append(df)
        if len(dataframes)>=1:    
            return pd.concat(dataframes, axis=0), "success"
        return None, "error"
        
    def calculate_balanced_month(self, months):
        current_date = datetime.now()
        first_day_of_month = current_date.replace(day=1)
        end_date = first_day_of_month + timedelta(days=months * 30)
        end_date = end_date.replace(day=1)

        first_day_of_month = first_day_of_month.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        start_date = pd.to_datetime(first_day_of_month, utc=True)
        end_date = pd.to_datetime(end_date, utc=True)

        return start_date, end_date