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
import datetime as datetime2


class LoadProfile:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the connection with database
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()


    def extraction(self, query_strings, dimension_check=False, pricing=False):
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
                and curvestart between 
                (select curvestart from trueprice.{control_area}_{curveType} where curvestart > '{curve_start} 00:00:00.000 +0500' limit 1) and 
                COALESCE( (select curvestart from trueprice.{control_area}_{curveType} where curvestart > '{curve_end} 00:00:00.000 +0500' limit 1), '9999-12-31 23:59:59.999 +0500');"""
            data_frame = None
            temp_time = time.time()
            data_frame = pl.read_database_uri(psql_query_data, str(self.engine.url), engine="connectorx")
            print("time complexity polars db data reading: ", time.time()-temp_time)
            psql_query_hierarchy = f"""select h.id, ca.name control_area, state.name state, lz.name load_zone, cz.name capacity_zone, u.name utility, strip.name strip, cg.name cost_group, cc.name cost_component , ct.name customer_type
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
                join trueprice.customer_type ct on ct.id = h.customer_type_id
                where h.id in ({', '.join(map(str, data_frame["hierarchy_id"].unique()))});"""
            temp_time = time.time()
            hierarchy_frame = pl.read_database_uri(psql_query_hierarchy, str(self.engine.url), engine="connectorx")
            print("time complexity polars db hierarchy reading: ", time.time()-temp_time)
            temp_time = time.time()
            merged_inner = data_frame.join(hierarchy_frame, left_on='hierarchy_id', right_on='id', how='inner')
            print("time complexity merging: ", time.time()-temp_time)
            if dimension_check:
                temp_time = time.time()
                pl_pivoted_df = merged_inner.pivot(
                    values="data",
                    index=["curvestart", "month", "he"],
                    columns=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'customer_type'],
                    aggregate_function="first"
                )
                pd_pivoted_df = pl_pivoted_df.to_pandas()
                pd_pivoted_df.set_index(['curvestart', 'month', 'he'], inplace=True)
                hierarchy = [ json.loads(i.replace('{', '[').replace('}', ']')) for i in pd_pivoted_df.columns]
                multi_index = pd.MultiIndex.from_tuples(hierarchy, names=["control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", "customer_type"])
                pd_pivoted_df.columns = multi_index
                print("time complexity polars pivoting: ", time.time()-temp_time)
                return pd_pivoted_df, "success"  
            elif pricing:
                tmp_time = time.time()
                start_date = datetime.strptime(start_date_stamp, "%Y%m%d").date()
                end_date = datetime.strptime(end_date_stamp, "%Y%m%d").date()
                df = pl.DataFrame(pl.datetime_range(start_date, end_date, datetime2.timedelta(hours=1), eager=True).alias(
                    "datemonth"
                ))

                # Add 'YearType' column: Leap or Non-Leap
                df = df.with_columns(
                    ((df['datemonth'].dt.year() % 4 == 0) & (
                        (df['datemonth'].dt.year() % 100 != 0) | (df['datemonth'].dt.year() % 400 == 0) )
                    ).map_elements(lambda x: 'Leap' if x else 'Non-Leap', return_dtype=pl.Utf8).alias('yeartype')
                )

                # Add 'Month' column: Extracting month from the datetime
                df = df.with_columns(df['datemonth'].dt.month().alias('Month'))

                # Add 'DayType' column: Weekday or Weekend
                df = df.with_columns(
                    df['datemonth'].dt.weekday().map_elements(lambda x: 'Weekend' if x >= 5 else 'Weekday', return_dtype=pl.Utf8).alias('daytype')
                )

                # Add 'HE' column: Hour number from 1 to 24
                df = df.with_columns((df['datemonth'].dt.hour() + 1).alias('he'))
                df = df.with_columns(pl.col("datemonth").dt.date().alias("datemonth"))
                print(len(df))
                print(time.time()-tmp_time)
                
                merged_inner = merged_inner.with_columns(
                    ((merged_inner['month'].dt.year() % 4 == 0) & (
                        (merged_inner['month'].dt.year() % 100 != 0) | (merged_inner['month'].dt.year() % 400 == 0) )
                    ).map_elements(lambda x: 'Leap' if x else 'Non-Leap', return_dtype=pl.Utf8).alias('yeartype')
                )

                # Add 'Month' column: Extracting month from the datetime
                merged_inner = merged_inner.with_columns(merged_inner['month'].dt.month().alias('Month'))

                # Add 'DayType' column: Weekday or Weekend
                merged_inner = merged_inner.with_columns(
                    merged_inner['month'].dt.weekday().map_elements(lambda x: 'Weekend' if x >= 5 else 'Weekday', return_dtype=pl.Utf8).alias('daytype')
                )

                # Add 'HE' column: Hour number from 1 to 24
                # merged_inner = merged_inner.with_columns((merged_inner['curvestart'].dt.hour() + 1).alias('HE'))
                merged_inner = merged_inner.with_columns(pl.col("month").dt.date().alias("datemonth"))
                merged_inner = merged_inner.with_columns(pl.col("he").cast(pl.Int8))
                merged_inner = merged_inner.groupby(
                    ["curvestart", "Month", "yeartype", "daytype", "he", "control_area", "state", "load_zone", "capacity_zone", "utility", "strip", "cost_group", "cost_component", 'customer_type']
                ).agg( pl.col("data").mean().alias("data") )
                df = df.join(merged_inner, on=["Month", "yeartype", "daytype", "he"], how='inner')
                df = df.to_pandas()
                return df, "success"  
            else:
                merged_inner = merged_inner.to_pandas()
                return merged_inner, "success"  
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
