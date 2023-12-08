"""
Implements the Extraction of Forward Curve Data from the database
"""

import pandas as pd
from datetime import datetime
from utils.database_connection import ConnectDatabase


class Matrix:
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

            if query_strings["curvestart"]:
                curve_start = str(datetime.strptime(query_strings["curvestart"], "%Y%m%d").date())
                curve_end = str(datetime.strptime(query_strings["curveend"], "%Y%m%d").date())
                
                operating_day_flag = True
            else:
                operating_day_flag = False
            

            if control_area not in ["nyiso", "miso", "ercot", "pjm", "isone"]:
                return None, "Unable to Fetch Results"
            
            elif control_area == "isone":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix 
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        UNION
                        select id, curvestart, curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix_history
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
                else:
                    psql_query = f"""
                        select id,    curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix 
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
            elif control_area == "pjm":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        UNION
                        select id, curvestart, curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix_history
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
                else:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
            elif control_area == "ercot":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        UNION
                        select id,   curvestart, curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix_history
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}' 
                        
                    """
                else:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
            elif control_area == "nyiso":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        UNION
                        select id, curvestart, curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix_history
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
                else:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """

            elif control_area == "miso":
                if query_strings["history"]:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        UNION
                        select id, curvestart, curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix_history
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
                else:
                    psql_query = f"""
                        select id, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component,term, beginning_date, load_profile, address, energy,
                                        variable_load_risk, line_losses, ncpc, da_economic, da_lscpr,
                                        rt_economic, rt_lscpr, ancillaries, regulation, fwd_reserve,
                                        rt_reserve, inadvertent_energy, marginal_loss_revenue_fund,
                                        price_responsive_demand, schedule_2_energy_admin_svc,
                                        schedule_3_reliability_admin_svc, gis, iso_fees, capacity,
                                        arr, rps_charge, renewable_power, sleeve_fee,
                                        utility_billing_surcharge, credit, other_1, other_2,
                                        total_full_requirements_price, cents, margin,
                                        total_bundled_price, total_contract_load from trueprice.matrix
                        where control_area_type = '{control_area}' and ({strip_query}) and beginning_date::date >= '{start_date}' and beginning_date::date <= '{end_date}'
                        
                    """
                

            if operating_day_flag:
                psql_query = f"""
                            {psql_query} and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                            """
            # end up the query
            psql_query =    f"""
                            {psql_query} order by curvestart desc,strip;
                            """
            data_frame = None
            data_frame = pd.read_sql_query(sql=psql_query, con=self.engine.connect())
            
            
            return data_frame, "success"  
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
