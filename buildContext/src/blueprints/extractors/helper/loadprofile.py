"""
Implements the Extraction of Forward Curve Data from the database
"""

import pandas as pd
from datetime import datetime
from utils.database_connection import ConnectDatabase
from sqlalchemy import text
import time
import polars as pl


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


    def extraction(self, query_strings):
        """
        Handling extraction for ancillarydata
        """
        try:
            time_temp = time.time()
            history = (query_strings["idcob"].lower() == 'all')
            cobonly = (query_strings["idcob"].lower() == 'cobonly')
            intradayonly  = (query_strings["idcob"].lower() == 'intradayonly')
            control_area = query_strings["iso"]
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
                psql_query = f"""
                select d.id, month, curvestart, he,
                data,
                ca.name control_area, state.name state, lz.name load_zone, cz.name capacity_zone, u.name utility, strip.name strip, cg.name cost_group, cc.name cost_component , ct.name customer_type
                from trueprice.loadprofile d
                join trueprice.hierarchy h on h.id = d.hierarchy_id
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
                where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                and LOWER(ca."name") = '{control_area}'
                order by curvestart;"""
                
                # testing query
                # psql_query = f"""
                #                 select d.id, month, curvestart, he,
                #                 data, 
                #                 ca.name control_area, state.name state, lz.name load_zone, cz.name capacity_zone, u.name utility, strip.name strip, cg.name cost_group, cc.name cost_component , ct.name customer_type
                #                 from trueprice.loadprofile d
                #                 join trueprice.hierarchy h on h.id = d.hierarchy_id 
                #                 join trueprice.curve_datatype cd on cd.id = h.curve_datatype_id 
                #                 join trueprice.control_area ca on ca.id = h.control_area_id 
                #                 join trueprice.state state on state.id = h.state_id  
                #                 join trueprice.load_zone lz on lz.id = h.load_zone_id  
                #                 join trueprice.capacity_zone cz on cz.id = h.capacity_zone_id 
                #                 join trueprice.utility u on u.id = h.utility_id 
                #                 join trueprice.block_type strip on strip.id = h.block_type_id  
                #                 join trueprice.cost_group cg on cg.id = h.cost_group_id 
                #                 join trueprice.cost_component cc on cc.id = h.cost_component_id 
                #                 join trueprice.customer_type ct on ct.id = h.customer_type_id 
                #                 where (LOWER(strip.name) = '7x24') and month::date >= '2020-01-01' and month::date <= '2030-02-01' and curvestart::date >= '2025-01-04' and curvestart::date <= '2025-01-05'
                #                 and LOWER(ca."name") = 'isone';"""
            data_frame = None
            # time_temp = time.time()
            # con=self.engine.connect()
            # result = con.execute(text(psql_query))
            # print('readtime complexity exec', time.time()-time_temp)
            # columns = result.keys()
            # print('readtime complexity keys', time.time()-time_temp)
            # rows = result.fetchall()
            # print('readtime complexity fetch', time.time()-time_temp)
            # df = pd.DataFrame(rows, columns=columns)
            # # df = pd.DataFrame(result.fetchall(), columns=result.keys())
            # print('readtime complexity con total', time.time()-time_temp)
            # time_temp = time.time()
            # data_frame = pd.read_sql_query(sql=text(psql_query), con=self.engine.connect())
            # print('readtime complexity pandas', time.time()-time_temp)
            time_temp = time.time()
            data_frame = pl.read_database_uri(psql_query, str(self.engine.url), engine="connectorx")
            data_frame = data_frame.to_arrow()
            data_frame = data_frame.to_pandas()
            print('readtime complexity polars', time.time()-time_temp)
            return data_frame, "success"  
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
