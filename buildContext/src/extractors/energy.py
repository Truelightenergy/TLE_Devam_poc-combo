"""
Implements the Extraction of Forward Curve Data from the database
"""

import pandas as pd
from datetime import datetime
from database_connection import ConnectDatabase


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
            control_area = query_strings["iso"]
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
            

            if control_area not in ["nyiso", "miso", "ercot", "pjm", "isone"]:
                return None, "Unable to Fetch Results"
            
            elif control_area == "nyiso":
                psql_query = f"""
                    select id, strip, cob, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount from trueprice.{control_area}_energy 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                    select id, strip, cob, curvestart, curveend, month, zone_a_amount, zone_b_amount, zone_c_amount, zone_d_amount, zone_e_amount, zone_f_amount, zone_g_amount, zone_h_amount, zone_i_amount, zone_j_amount, zone_k_amount from trueprice.{control_area}_energy_history
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by cob,curvestart desc,strip;
                """
            elif control_area == "miso":
                psql_query = f"""
                    select id, strip, cob, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, amilcips_amount, amilcilco_amount, amilip_amount, indy_amount from trueprice.{control_area}_energy 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                    select id, strip, cob, curvestart, curveend, month, amilcips_amount, amilcilco_amount, amilip_amount, indy_amount from trueprice.{control_area}_energy_history
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by cob,curvestart desc,strip;
                """
                
            elif control_area == "ercot":
                psql_query = f"""
                    select id, strip, cob, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, north_amount, houston_amount, south_amount, west_amount from trueprice.{control_area}_energy 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                    select id, strip, cob, curvestart, curveend, month, north_amount, houston_amount, south_amount, west_amount from trueprice.{control_area}_energy_history 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by cob,curvestart desc,strip;
                    """
                
            elif control_area == "pjm":
                psql_query = f"""
                    select id, strip, cob,  curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, aeco_amount, aep_amount, aps_amount, atsi_amount, bge_amount, comed_amount, day_amount, deok_amount, dom_amount, dpl_amount, duq_amount, jcpl_amount, meted_amount, peco_amount, penelec_amount, pepco_amount, ppl_amount, pseg_amount, reco_amount, west_amount, ad_amount, ni_amount, east_amount from trueprice.{control_area}_energy 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                    select id, strip, cob,  curvestart, curveend, month, aeco_amount, aep_amount, aps_amount, atsi_amount, bge_amount, comed_amount, day_amount, deok_amount, dom_amount, dpl_amount, duq_amount, jcpl_amount, meted_amount, peco_amount, penelec_amount, pepco_amount, ppl_amount, pseg_amount, reco_amount, west_amount, ad_amount, ni_amount, east_amount from trueprice.{control_area}_energy_history 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by cob,curvestart desc,strip;
                    """
                
                
            elif control_area == "isone":
                psql_query = f"""
                    select id, strip, cob, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, maine_amount, newhampshire_amount, vermont_amount, connecticut_amount, rhodeisland_amount, semass_amount, wcmass_amount, nemassbost_amount from trueprice.{control_area}_energy 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                    select id, strip, cob, curvestart, curveend, month, maine_amount, newhampshire_amount, vermont_amount, connecticut_amount, rhodeisland_amount, semass_amount, wcmass_amount, nemassbost_amount from trueprice.{control_area}_energy_history 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by cob,curvestart desc,strip;
                    """
                
            data_frame = None
            data_frame = pd.read_sql_query(sql=psql_query, con=self.engine.connect())
            return data_frame, "success"  
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
