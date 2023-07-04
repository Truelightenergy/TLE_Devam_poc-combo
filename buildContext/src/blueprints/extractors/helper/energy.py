"""
Implements the Extraction of Forward Curve Data from the database
"""

import pandas as pd
from datetime import datetime
from utils.database_connection import ConnectDatabase


class Energy:
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
            control_area = str(query_strings["iso"]).lower()
            strips = query_strings["strip"]
            strip_filters = list()
            for strip in strips:
                strip = strip.split("_")[-1]
                strip_filters.append(f"LOWER(strip) = '{strip.lower()}'")
            strip_query = " OR ".join(strip_filters)
            start_date_stamp = query_strings["start"]
            end_date_stamp = query_strings["end"]

            start_date = str(datetime.strptime(start_date_stamp, "%Y%m%d").date())
            end_date = str(datetime.strptime(end_date_stamp, "%Y%m%d").date())

            curve_start = str(datetime.strptime(query_strings["curvestart"], "%Y%m%d").date())
            curve_end = str(datetime.strptime(query_strings["curveend"], "%Y%m%d").date())

            

            if control_area not in ["nyiso", "miso", "ercot", "pjm", "isone"]:
                return None, "Unable to Fetch Results"
            
            elif control_area == "isone":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, cob,  month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        UNION
                        select id, cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy_history
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
                else:
                    psql_query = f"""
                        select id, cob,  month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
            elif control_area == "pjm":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        UNION
                        select id, cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy_history
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
                else:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
            elif control_area == "ercot":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        UNION
                        select id, cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy_history
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}' 
                        order by curvestart desc,strip;
                    """
                else:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
            elif control_area == "nyiso":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        UNION
                        select id, cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy_history
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
                else:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """

            elif control_area == "miso":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        UNION
                        select id, cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy_history
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
                else:
                    psql_query = f"""
                        select id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                        order by curvestart desc,strip;
                    """
                
            data_frame = None
            data_frame = pd.read_sql_query(sql=psql_query, con=self.engine.connect())
            
            
            return data_frame, "success"  
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
