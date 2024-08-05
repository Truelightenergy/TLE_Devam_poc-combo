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


class LineLoss:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the connection with database
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()


    def extraction(self, query_strings):
        """
        Handling extraction for ancillarydata
        """
        try:
            time_temp = time.time()
            # history = (query_strings["idcob"].lower() == 'all')
            # cobonly = (query_strings["idcob"].lower() == 'cobonly')
            # intradayonly  = (query_strings["idcob"].lower() == 'intradayonly')
            curveType = query_strings["curve_type"]

            if query_strings["curvestart"]:
                curve_start = str(datetime.strptime(query_strings["curvestart"], "%Y%m%d").date())
                curve_end = str(datetime.strptime(query_strings["curveend"], "%Y%m%d").date())
                
                operating_day_flag = True
            else:
                operating_day_flag = False
            
            psql_query_data = f"""select *
            from trueprice.{curveType} d
            where curvestart between 
            (select curvestart from trueprice.{curveType} where curvestart > '{curve_start} 00:00:00.000 +0500' order by curvestart limit 1) and 
            (select curvestart from trueprice.{curveType} where curvestart > '{curve_end} 00:00:00.000 +0500' order by curvestart limit 1);"""
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
            merged_inner = merged_inner.to_pandas()
            return merged_inner, "success"  
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
