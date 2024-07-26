"""
Implements the Extraction of Forward Curve Data from the database
"""

import pandas as pd
from datetime import datetime
from utils.database_connection import ConnectDatabase
from sqlalchemy import text
import time
import polars as pl
import json


class Vlr:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the connection with database
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()


    def extraction(self, query_strings, dimension_check=False):
        """
        Handling extraction for ancillarydata
        """
        try:
            time_temp = time.time()
            history = (query_strings["idcob"].lower() == 'all')
            cobonly = (query_strings["idcob"].lower() == 'cobonly')
            intradayonly  = (query_strings["idcob"].lower() == 'intradayonly')
            control_area = query_strings["iso"]
            curveType = query_strings["curve_type"]
            strips = query_strings["strip"]
            strip_filters = list()
            # normal_strip = False
            strip_query = ''
            # psql_query_7x24 = ''
            # psql_query_7x24_hist = ''
            for strip in strips:
                strip = strip.split("_")[-1]
                # if '7x24' in strip:
                #     normal_strip = True
                #     continue
                strip_filters.append(f"LOWER(strip.name) = '{strip.lower()}'")
            if strip_filters:
                strip_query = '(' + " OR ".join(strip_filters) + ') and'
            else:
                strip_query = "(LOWER(strip) = 'none') and"
            start_date_stamp = query_strings["start"]
            end_date_stamp = query_strings["end"]

            start_year = datetime.strptime(start_date_stamp, "%Y%m%d").year
            end_year = datetime.strptime(end_date_stamp, "%Y%m%d").year
            start_month = datetime.strptime(start_date_stamp, "%Y%m%d").month
            end_month = datetime.strptime(end_date_stamp, "%Y%m%d").month

            if query_strings["curvestart"]:
                curve_start = str(datetime.strptime(query_strings["curvestart"], "%Y%m%d").date())
                curve_end = str(datetime.strptime(query_strings["curveend"], "%Y%m%d").date())
                
                operating_day_flag = True
            else:
                operating_day_flag = False

            if control_area not in ["isone", "pjm", "ercot", "nyiso", "miso"]:
                return None, "Unable to Fetch Results"
            else:
                psql_query_data = f"""select *
                from trueprice.{control_area}_{curveType} d
                where curvestart between 
                (select curvestart from trueprice.{control_area}_{curveType} where curvestart > '{curve_start} 00:00:00.000 +0500' limit 1) and 
                (select curvestart from trueprice.{control_area}_{curveType} where curvestart > '{curve_end} 00:00:00.000 +0500' limit 1);"""
            data_frame = None
            temp_time = time.time()
            data_frame = pl.read_database_uri(psql_query_data, str(self.engine.url), engine="connectorx")
            print("time complexity polars db data reading: ", time.time()-temp_time)
            psql_query_hierarchy = f"""select h.id, ca.name control_area, state.name state, lz.name load_zone, cz.name capacity_zone, u.name utility, strip.name strip, cg.name cost_group, cc.name cost_component
                from trueprice.hierarchy h
                join trueprice.curve_datatype cd on cd.id = h.curve_datatype_id 
                join trueprice.control_area ca on ca.id = h.control_area_id 
                join trueprice.state state on state.id = h.state_id  
                join trueprice.load_zone lz on lz.id = h.load_zone_id  
                join trueprice.capacity_zone cz on cz.id = h.capacity_zone_id 
                join trueprice.utility u on u.id = h.utility_id 
                join trueprice.block_type strip on strip.id = h.block_type_id  
                join trueprice.cost_group cg on cg.id = h.cost_group_id 
                join trueprice.cost_component cc on cc.id = h.cost_component_id 
                where h.id in ({', '.join(map(str, data_frame["hierarchy_id"].unique()))});"""
            temp_time = time.time()
            hierarchy_frame = pl.read_database_uri(psql_query_hierarchy, str(self.engine.url), engine="connectorx")
            print("time complexity polars db hierarchy reading: ", time.time()-temp_time)
            temp_time = time.time()
            merged_inner = data_frame.join(hierarchy_frame, left_on='hierarchy_id', right_on='id', how='inner')
            print("time complexity merging: ", time.time()-temp_time)

            # # Define the range of years
            # years = list(range(start_year, end_year+1))
            # # Define months and hours
            # months = list(range(1, 13))
            # hours = list(range(1, 25))
            # # Generate all combinations of years, months, and hours
            # data = [(year, month, hour) for year in years for month in months for hour in hours]
            # # Create the DataFrame
            # df = pl.DataFrame(data, schema=["year", "datemonth", "he"])
            # df = df.filter((pl.col("year") > start_year) | ((pl.col("year") == start_year) & (pl.col("datemonth") >= start_month)))
            # df = df.filter((pl.col("year") < end_year) | ((pl.col("year") == end_year) & (pl.col("datemonth") <= end_month)))
            # df = df.with_columns(pl.col(["datemonth", "he"]).cast(pl.Int32))
            # df = df.join(merged_inner, on=['datemonth', 'he'], how='left')
            if dimension_check:
                temp_time = time.time()
                pl_pivoted_df = merged_inner.pivot(
                    values="data",
                    index=["curvestart", 'year', "datemonth", "he"],
                    columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component"],
                    aggregate_function="first"
                )
                pd_pivoted_df = pl_pivoted_df.to_pandas()
                pd_pivoted_df.set_index(['curvestart', 'year', 'datemonth', 'he'], inplace=True)
                hierarchy = [ json.loads(i.replace('{', '[').replace('}', ']')) for i in pd_pivoted_df.columns]
                multi_index = pd.MultiIndex.from_tuples(hierarchy, names=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component"])
                pd_pivoted_df.columns = multi_index
                print("time complexity polars pivoting: ", time.time()-temp_time)
                return pd_pivoted_df, "success"  
            else:
                df = merged_inner.to_pandas()
                return df, "success"  
        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
