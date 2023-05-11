"""
Implements the Extraction of Rec data details from the database
"""

import pandas as pd
from datetime import datetime
from database_connection import ConnectDatabase


class Rec:
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
        Handling extraction for recdata
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
            
            if control_area not in ["nyiso", "ercot", "pjm", "isone"]:
                return None, "Unable to Fetch Results"

            elif control_area == "pjm":
                psql_query = f"""
                     select id, strip, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, Month, NJ_Total_Cost_per_MWh_amount, NJ_Solar_percent, NJ_Solar_amount, NJ_Class_I_percent, NJ_Class_I_amount, 
                            NJ_Class_II_percent, NJ_Class_II_amount, OH_Total_Cost_per_MWh_amount, OH_Solar_percent, OH_Solar_In_State_amount,
                            OH_Solar_Adj_amount, OH_RECs_percent, OH_In_State_amount, OH_Adj_amount, PA_Total_Cost_per_MWh_amount,
                            PA_Solar_percent, PA_Solar_amount, PA_Tier_I_percent, PA_Tier_I_amount, PA_Tier_II_percent, PA_Tier_II_amount,
                            MD_Total_Cost_per_MWh_amount, MD_Solar_percent, MD_Solar_amount, MD_Tier_I_percent, MD_Tier_I_amount, 
                            MD_Tier_II_percent, MD_Tier_II_amount, DC_Total_Cost_per_MWh_amount, DC_Solar_percent, DC_Solar_amount,
                            DC_Tier_I_percent, DC_Tier_I_amount, DC_Tier_II_percent, DC_Tier_II_amount, DE_Total_Cost_per_MWh_amount,
                            DE_Solar_percent, DE_Solar_amount, DE_RECs_percent, DE_REC_amount, IL_Total_Cost_per_MWh_amount,
                            IL_PER_o_load_covered_by_Supplier_vs_Utility_percent, IL_Total_Standard_percent, IL_Solar_percent,
                            IL_Solar_amount, IL_Wind_percent, IL_Wind_amount, IL_ACP_percent, IL_ACP_amount from trueprice.{control_area}_rec 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                     select id, strip, curvestart, curveend, Month, NJ_Total_Cost_per_MWh_amount, NJ_Solar_percent, NJ_Solar_amount, NJ_Class_I_percent, NJ_Class_I_amount, 
                            NJ_Class_II_percent, NJ_Class_II_amount, OH_Total_Cost_per_MWh_amount, OH_Solar_percent, OH_Solar_In_State_amount,
                            OH_Solar_Adj_amount, OH_RECs_percent, OH_In_State_amount, OH_Adj_amount, PA_Total_Cost_per_MWh_amount,
                            PA_Solar_percent, PA_Solar_amount, PA_Tier_I_percent, PA_Tier_I_amount, PA_Tier_II_percent, PA_Tier_II_amount,
                            MD_Total_Cost_per_MWh_amount, MD_Solar_percent, MD_Solar_amount, MD_Tier_I_percent, MD_Tier_I_amount, 
                            MD_Tier_II_percent, MD_Tier_II_amount, DC_Total_Cost_per_MWh_amount, DC_Solar_percent, DC_Solar_amount,
                            DC_Tier_I_percent, DC_Tier_I_amount, DC_Tier_II_percent, DC_Tier_II_amount, DE_Total_Cost_per_MWh_amount,
                            DE_Solar_percent, DE_Solar_amount, DE_RECs_percent, DE_REC_amount, IL_Total_Cost_per_MWh_amount,
                            IL_PER_o_load_covered_by_Supplier_vs_Utility_percent, IL_Total_Standard_percent, IL_Solar_percent,
                            IL_Solar_amount, IL_Wind_percent, IL_Wind_amount, IL_ACP_percent, IL_ACP_amount from trueprice.{control_area}_rec_history
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by curvestart desc,strip;
                """
            elif control_area == "isone":
                psql_query = f"""
                    select id, strip, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, ct_total_cost_per_mwh, ct_class_i, ct_class_i_price,
                        ct_class_ii, ct_class_ii_price, ct_class_iii,
                        ct_class_iii_price, ma_total_cost_per_mwh, ma_rps_class_i_total,
                        ma_rps_class_i, ma_class_i_price, ma_solar_carve_out_i,
                        ma_srec_i_price, ma_solar_carve_out_ii, ma_srec_ii_price,
                        ma_class_ii_non_waste, ma_class_ii_nw_price, ma_class_ii_waste,
                        ma_class_ii_waste_price, ma_aps, ma_aps_price,
                        ma_ces_obligation, ma_ces_less_rps_i_, ma_ces_price, ma_cps,
                        ma_cps_price, ma_ces_e, ma_ces_e_price, nh_total_cost_per_mwh,
                        nh_class_i_total, nh_class_i, nh_class_i_price,
                        nh_class_i_thermal, nh_class_i_thermal_price, nh_class_ii,
                        nh_class_ii_price, nh_class_iii, nh_class_iii_price,
                        nh_class_iv, nh_class_iv_price, me_total_cost_per_mwh,
                        me_new_and_1a_total, me_1a, me_1a_acp, me_class_1,
                        me_class_1_price, me_thermal, me_thermal_price, me_class_2,
                        me_class_2_price, ri_total_cost_per_mwh, ri_new, ri_new_price,
                        ri_existing, ri_existing_price from trueprice.{control_area}_rec 
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                    select id, strip, curvestart, curveend, month, ct_total_cost_per_mwh, ct_class_i, ct_class_i_price,
                            ct_class_ii, ct_class_ii_price, ct_class_iii,
                            ct_class_iii_price, ma_total_cost_per_mwh, ma_rps_class_i_total,
                            ma_rps_class_i, ma_class_i_price, ma_solar_carve_out_i,
                            ma_srec_i_price, ma_solar_carve_out_ii, ma_srec_ii_price,
                            ma_class_ii_non_waste, ma_class_ii_nw_price, ma_class_ii_waste,
                            ma_class_ii_waste_price, ma_aps, ma_aps_price,
                            ma_ces_obligation, ma_ces_less_rps_i_, ma_ces_price, ma_cps,
                            ma_cps_price, ma_ces_e, ma_ces_e_price, nh_total_cost_per_mwh,
                            nh_class_i_total, nh_class_i, nh_class_i_price,
                            nh_class_i_thermal, nh_class_i_thermal_price, nh_class_ii,
                            nh_class_ii_price, nh_class_iii, nh_class_iii_price,
                            nh_class_iv, nh_class_iv_price, me_total_cost_per_mwh,
                            me_new_and_1a_total, me_1a, me_1a_acp, me_class_1,
                            me_class_1_price, me_thermal, me_thermal_price, me_class_2,
                            me_class_2_price, ri_total_cost_per_mwh, ri_new, ri_new_price,
                            ri_existing, ri_existing_price from trueprice.{control_area}_rec_history
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by curvestart desc,strip;
                """
            elif control_area == "nyiso":
                psql_query = f"""
                    select id, strip, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, ny_total_cost_per_mwh, ny_class_i, ny_class_i_price,
                        ny_class_ii, ny_class_ii_price, ny_total_cost_per_mwh_zec_rate, ny_class_iii_zec, ny_class_iii_price from trueprice.{control_area}_rec 
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    UNION
                    select id, strip, curvestart, curveend, month, ny_total_cost_per_mwh, ny_class_i, ny_class_i_price,
                            ny_class_ii, ny_class_ii_price, ny_total_cost_per_mwh_zec_rate, ny_class_iii_zec, ny_class_iii_price from trueprice.{control_area}_rec_history
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by curvestart desc,strip;
                """
            elif control_area == "ercot":
                psql_query = f"""
                    select id, strip, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, month, tx_total_cost_per_mWh, tx_compliance, tx_rec_price, tx_year,
                        tx_total_texas_competitive_load_mWh, tx_rps_mandate_mWh, tx_prct from trueprice.{control_area}_rec
                        where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}' 
                    UNION
                    select id, strip, curvestart, curveend, month, tx_total_cost_per_mWh, tx_compliance, tx_rec_price, tx_year,
                        tx_total_texas_competitive_load_mWh, tx_rps_mandate_mWh, tx_prct from trueprice.{control_area}_rec_history
                    where ({strip_query}) and month::date >= '{start_date}' and month::date <= '{end_date}'
                    order by curvestart desc,strip;
                """

            data_frame = None
            psql_query = f"select * from trueprice.{control_area}_rec where LOWER(strip) = '{strip.lower()}' and month::date >= '{start_date}' and month::date <= '{end_date}';"
            data_frame = pd.read_sql_query(sql=psql_query, con=self.engine.connect())
            return data_frame, "success"  
  
        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
