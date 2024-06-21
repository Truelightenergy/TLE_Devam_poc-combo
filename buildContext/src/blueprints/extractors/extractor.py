"""
makes query to the database and returns to the database
"""

import numpy as np
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
from .helper.loadprofile import LoadProfile
import time


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
        self.loadprofile = LoadProfile()
        self.filter = Rules()

    def post_processing_csv(self, df, type):
        """
        post process the dataframe
        """

        if type == 'headroom':
            # df = df.transpose()
            df["ptc"] = df["ptc"] * 1000
            df["total_bundled_price"] = df["total_bundled_price"]* 1000
            df["headroom"] = df["headroom"]* 1000
            df['curvestart'] = df['curvestart'].dt.strftime('%m/%d/%Y')

            df = df[["control_area", "state", "utility","load_zone", "load_profile","curvestart", "month", "ptc",  "term",  "beginning_date", "total_bundled_price", "headroom", "headroom_prct"]]
            df.columns = ["ISO ", "State", "Utility","Load Zone", "Load Profile","Headroom Effective Date", "PTC Effective Date", "Utility PTC ($/MWh)", "TLE Price Term (months)", "TLE Price Start Date", "Truelight Price ($/MWh)", "Headroom ($/MWh)", "Headrrom (%)"]
            return df

        elif type=='matrix':
            # Assuming df is your DataFrame
            # Using pivot_table to handle potential duplicate entries
          
            # df.columns = ["matching_id", "lookup_id", "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "term", "beginning_date", "load_profile", "sub_cost_component", "data"]
            pivot_df = df.pivot_table(index=["matching_id", "lookup_id","control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "term", "beginning_date", "load_profile"],
                                    columns="sub_cost_component",
                                    values="data",
                                    aggfunc="first",  # You can choose an appropriate aggregation function
                                    fill_value=0)  # Replace NaN with 0 or choose another fill value

            # Resetting index to make the columns flat
            reshaped_df = pivot_df.reset_index()
           
            # Display the reshaped DataFrame
            reshaped_df = reshaped_df.transpose()
            # reshaped_df = reshaped_df.drop(0)

            # If you want to reset the index after removing the row
            reshaped_df=reshaped_df.rename_axis(None)
            reshaped_df = reshaped_df.iloc[2:, :]
            return reshaped_df

            
        elif type == 'ptc':
            pivoted_df = pd.pivot_table(df, values='data', index=['curvestart', 'month'], columns=["matching_id", "lookup_id", "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "control_area_type", "utility_name", "profile_load"], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
           
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())
           
           
            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'matching_id' : 'Matching ID', 'lookup_id': 'Lookup ID', 'curvestart': 'Curve Update Date', 'month': "Curve Start Month"})
            # renaming columns
            flattened_df.columns.names =  ["Matching ID", "Lookup ID", "Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", "Control_area_type", "Utility_name", "Profile_load"]
            
            #remove matching id and lookup id, Control_area_type, Utility_name  rows.
            flattened_df.columns = flattened_df.columns.droplevel([0, 1, 10,11])
            # returning dataframe
            return flattened_df
        
        elif type =="energy":
            pivoted_df = pd.pivot_table(df, values='data', index=['curvestart', 'month', 'cob'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "my_order", "strip", "cost_group", "cost_component", 'sub_cost_component'], aggfunc=list)
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Update Date', 'month': "Curve Start Month" , 'cob': 'COB'})
            flattened_df = flattened_df.droplevel('my_order', axis=1)
            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", " "]
            
            # returning dataframe
            return flattened_df
        
        elif type =="nonenergy":
            pivoted_df = pd.pivot_table(df, values='data', index=['curvestart', 'month'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "my_order", "strip", "cost_group", "cost_component", 'sub_cost_component'], aggfunc=list) #, "distribution_category"
            pivoted_df.columns.name = None
            pivoted_df.index.name = None
            
            # Explode the lists into multiple rows
            flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())
            flattened_df = flattened_df.droplevel('my_order', axis=1)

            # rename indexes
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Update Date', 'month': "Curve Start Month"})

            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", " "] #, "Normal Type"
            
            # returning dataframe
            return flattened_df
        
        elif type =="loadprofile":
            # temp_time = time.time()
            # pivoted_df = pd.pivot_table(df, values='data', index=['curvestart', 'month', 'he'], columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'customer_type'], aggfunc=list) #, "distribution_category"
            # print("Pivot pandas time complexity", time.time()-temp_time)
            # pivoted_df.columns.name = None
            # pivoted_df.index.name = None
            
            # # Explode the lists into multiple rows
            # flattened_df = pivoted_df.apply(lambda x: pd.Series(x).explode())

            # rename indexes
            flattened_df = df
            flattened_df = flattened_df.rename_axis(index={'curvestart': 'Curve Update Date', 'month': "Curve Start Month", "he": "HE"})

            # renaming columns
            flattened_df.columns.names =  ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", "Customer Type"] #, "Normal Type"
            
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
    
    def post_processing_json(self, df,type):
        """
        post process the dataframe
        """
        try:
            if type == 'headroom':
                columns=["control_area", "state", "utility","load_zone", "load_profile","curvestart", "month", "ptc",  "term",  "beginning_date", "total_bundled_price", "headroom", "headroom_prct"]
                df= df[columns]
                df = df.copy()
               
                df["ptc"] = df["ptc"] * 1000
                df["total_bundled_price"] = df["total_bundled_price"]* 1000
                df["headroom"] = df["headroom"]* 1000
                df['curvestart'] = df['curvestart'].dt.strftime('%m/%d/%Y')
                
                df.columns = ["ISO ", "State", "Utility","Load Zone", "Load Profile","Headroom Effective Date", "PTC Effective Date", "Utility PTC ($/MWh)", "TLE Price Term (months)", "TLE Price Start Date", "Truelight Price ($/MWh)", "Headroom ($/MWh)", "Headrrom (%)"]
                return df
            
            elif type=='matrix':
                columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "term", "beginning_date", "load_profile"]
                df= df[columns]
                df = df.copy()
                df.columns = columns
            
            elif type == 'ptc':
                columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "profile_load"]
                df= df[columns]
                df = df.copy()
                df.columns = columns
                           
            elif type == 'loadprofile':
                columns=["month", "he", 'data', 'curvestart', "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'customer_type']

                df= df[columns]
                df = df.copy()
                if not df.empty:
                    df["curvestart"] = df["curvestart"].dt.strftime('%Y-%m-%d %H:%M:%S')
                    df["month"] = df["month"].dt.strftime('%Y-%m-%d %H:%M:%S')


                df.columns = ["Curve Start Month", "HE", 'Data', 'Curve Update Date', "Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", 'Customer Type']

            else:
                columns=["month", 'data', 'curvestart', "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'sub_cost_component']

                df= df[columns]
                df = df.copy()
                if not df.empty:
                    df["curvestart"] = df["curvestart"].dt.strftime('%Y-%m-%d %H:%M:%S')
                    df["month"] = df["month"].dt.strftime('%Y-%m-%d %H:%M:%S')


                df.columns = ["Curve Start Month", 'Data', 'Curve Update Date', "Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component", 'Sub Cost Component']
                
            return df   
        except Exception as e:
            print(e)
            return None

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
            elif str(query_strings["curve_type"]).lower() == "loadprofile":
                dataframe, status = self.loadprofile.extraction(query_strings, download_type.lower() in ("csv", "xlsx")) 

            if not isinstance(dataframe, pd.DataFrame):
                    return dataframe, status
            
            
            control_table = f"{query_strings['iso']}_{query_strings['curve_type']}"
            email = session["user"]
            if session["level"]!= 'admin':
                rules = self.filter.filter_data(control_table, email)
                dataframe, status = self.dataframe_filtering(dataframe, rules, control_table)
            
                if status != "success":
                    return None, "No Subscription available"

            if download_type.lower() in ("csv", "xlsx"):
                dataframe = self.post_processing_csv(dataframe, str(query_strings["curve_type"]).lower())
            else:
                dataframe = self.post_processing_json(dataframe,str(query_strings["curve_type"]).lower())
            
            
                
            return dataframe, status
        except:
            return None, "Unable to Fetch Data"

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