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


class Shaping:
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
            strips = [i.split('_')[-1].lower() for i in strips]
            # strip_filters = list()
            # normal_strip = False
            # strip_query = ''
            # psql_query_7x24 = ''
            # psql_query_7x24_hist = ''
            # for strip in strips:
            #     strip = strip.split("_")[-1]
            #     # if '7x24' in strip:
            #     #     normal_strip = True
            #     #     continue
            #     strip_filters.append(f"LOWER(strip.name) = '{strip.lower()}'")
            # if strip_filters:
            #     strip_query = '(' + " OR ".join(strip_filters) + ') and'
            # else:
            #     strip_query = "(LOWER(strip) = 'none') and"
            start_date_stamp = query_strings["start"]
            end_date_stamp = query_strings["end"]

            start_date = str(datetime.strptime(start_date_stamp, "%Y%m%d").date())
            end_date = str(datetime.strptime(end_date_stamp, "%Y%m%d").date())

            if query_strings["curvestart"]:
                curve_start = str(datetime.strptime(query_strings["curvestart"], "%Y%m%d").date())
                curve_end = str(datetime.strptime(query_strings["curveend"], "%Y%m%d").date())
                
                operating_day_flag = True
            else:
                operating_day_flag = False

            if control_area not in ["isone", "pjm", "ercot", "nyiso", "miso"]:
                return None, "Unable to Fetch Results"
            else:
                # Original query::: , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend
                # psql_query_data = f"""
                # select * from trueprice.{control_area}_{curveType} d
                # where "month" between '{start_date} 00:00:00.000 +0500' and '{end_date} 00:00:00.000 +0500' 
                # and curvestart between '{curve_start}' and '{curve_end}';"""
                psql_query_data = f"""select *
                from trueprice.{control_area}_{curveType} d
                where "month" between '{start_date} 00:00:00.000 +0500' and '{end_date} 00:00:00.000 +0500' 
                and curvestart between '{curve_start} 00:00:00.000 +0500' and '{curve_end} 23:59:59.999 +0500';"""
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

            # if '7x24' in strips:
            #     temp_time = time.time()
            #     filtered = merged_inner.filter(pl.col("strip").str.contains("2x16|5x16|7x8"))
            #     sql_query_monthly_reference_data = f"""
            #         SELECT *
            #         FROM trueprice.monthly_reference_data
            #         WHERE 
            #             "ISO" = '{control_area.upper()}'
            #             AND "CalMonth" >= '{start_date[:7]}'
            #             AND "CalMonth" <= '{end_date[:7]}';"""
            #     monthly_reference_data = pl.read_database_uri(sql_query_monthly_reference_data, str(self.engine.url), engine="connectorx")
            #     filtered = filtered.with_columns( pl.col('month').apply(lambda x: x.strftime('%Y-%m'), return_dtype=pl.Utf8).alias('CalMonth') )
            #     filtered = filtered.join(monthly_reference_data, on='CalMonth', how='inner')
            #     filtered = filtered.with_columns(
            #         pl.when(pl.col("strip").str.contains("2x16"))
            #         .then(pl.col("data") * pl.col("2x16"))
            #         .when(pl.col("strip").str.contains("5x16"))
            #         .then(pl.col("data") * pl.col("5x16"))
            #         .when(pl.col("strip").str.contains("7x8"))
            #         .then(pl.col("data") * pl.col("7x8"))
            #         .otherwise(pl.col("data"))
            #         .alias("data")
            #     )
            #     filtered = filtered.with_columns(pl.lit("7x24").alias("strip"))
            #     filtered = filtered.groupby(
            #         ["curvestart", "month", "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "7x24"]
            #     ).agg( pl.col("data").sum().alias("data") )
            #     filtered = filtered.with_columns((pl.col("data") / pl.col("7x24")).alias("data"))
            #     merged_inner = merged_inner.drop(['id', 'hierarchy_id'])
            #     # filtered = filtered.drop(['7x24'])
            #     filtered = filtered[merged_inner.columns]
            #     merged_inner = pl.concat([merged_inner, filtered])
            #     print("time complexity polars db hierarchy reading: ", time.time()-temp_time)
            
            merged_inner = merged_inner.filter(pl.col("strip").str.contains("|".join(strips)))
            if dimension_check:
                temp_time = time.time()
                pl_pivoted_df = merged_inner.pivot(
                    values="data",
                    # index=["curvestart", "month", "year", "datemonth", "weekday", "he"],
                    index=["curvestart", "month", 'he'],
                    columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component"],
                    aggregate_function="first"
                )
                pd_pivoted_df = pl_pivoted_df.to_pandas()
                # pd_pivoted_df.set_index(["curvestart", "month", "year", "datemonth", "weekday", "he"], inplace=True)
                pd_pivoted_df.set_index(["curvestart", "month", 'he'], inplace=True)
                hierarchy = [ json.loads(i.replace('{', '[').replace('}', ']')) for i in pd_pivoted_df.columns]
                multi_index = pd.MultiIndex.from_tuples(hierarchy, names=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component"])
                pd_pivoted_df.columns = multi_index
                print("time complexity polars pivoting: ", time.time()-temp_time)
                return pd_pivoted_df, "success"  
            else:
                merged_inner = merged_inner.to_arrow()
                merged_inner = merged_inner.to_pandas()
                return merged_inner, "success"
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
