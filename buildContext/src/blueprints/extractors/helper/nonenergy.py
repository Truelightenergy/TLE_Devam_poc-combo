"""
Implements the Extraction of non energy details from the database
"""

import pandas as pd
from datetime import datetime
from utils.database_connection import ConnectDatabase
from sqlalchemy import text


class NonEnergy:
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
            normal_strip = False
            strip_query = ''
            psql_query_7x24 = ''
            psql_query_7x24_hist = ''
            for strip in strips:
                strip = strip.split("_")[-1]
                if '7x24' in strip:
                    normal_strip = True
                    # continue
                strip_filters.append(f"LOWER(strip) = '{strip.lower()}'")
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
            
            elif control_area == "isone":
                if query_strings["history"]:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        UNION
                        select 'Distributed' "my_order",id, month, curvestart, curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data",
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy_history e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                    
                    psql_query_7x24_hist = f"""
                                        UNION
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy_history where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                else:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """

            elif control_area == "pjm":
                if query_strings["history"]:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        UNION
                        select 'Distributed' "my_order",id, month, curvestart, curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data",
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy_history e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                    
                    psql_query_7x24_hist = f"""
                                        UNION
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy_history where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                else:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
            elif control_area == "ercot":
                if query_strings["history"]:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        UNION
                        select 'Distributed' "my_order",id, month, curvestart, curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data",
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy_history e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                    
                    psql_query_7x24_hist = f"""
                                        UNION
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy_history where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                else:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
            elif control_area == "nyiso":
                if query_strings["history"]:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        UNION
                        select 'Distributed' "my_order",id, month, curvestart, curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data",
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy_history e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                    
                    psql_query_7x24_hist = f"""
                                        UNION
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy_history where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                else:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
            elif control_area == "miso":
                if query_strings["history"]:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        UNION
                        select 'Distributed' "my_order",id, month, curvestart, curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data",
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy_history e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                    
                    psql_query_7x24_hist = f"""
                                        UNION
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy_history where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                else:
                    psql_query = f"""
                        select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                        case
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'reactive supply value%' or
                        LOWER(cost_component) like 'teac%' or 
                        LOWER(cost_component) like 'nits rate%' or
                        LOWER(cost_component) like 'arr credit%' )
                        then (data/r."7x24")*1000
                        when LOWER("strip") = '7x24' and 
                        (LOWER(cost_component) like 'black start charge%')
                        then (data/r."7x24")
                        else data
                        end as "data", 
                        control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                        from trueprice.{control_area}_nonenergy e
                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                        where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}'
                        
                    """
                    psql_query_7x24 = f"""
                                        union all
                                        select 'Normalized' "my_order", row_number() over () as id,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                                        ROUND((sum(case
                                        when LOWER(e."strip") = '2x16' then e."data" * r."2x16"
                                        when LOWER(e."strip") = '5x16' then e."data" * r."5x16"
                                        when LOWER(e."strip") = '7x8' then e."data" * r."7x8"
                                        when LOWER(e."strip") = 'we' then e."data" * r."WE"
                                        when LOWER(e."strip") = 'wd' then e."data" * r."WD"
                                        end)/r."7x24")::numeric,2) as "data" ,
                                        control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,cost_component ,sub_cost_component
                                        from 
                                        (
                                        select 
                                        case 
                                        when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                                        when LOWER("strip") in ('wd', 'we') then 'wd' 
                                        else 'ph' 
                                        end as distribution_category, 
                                        * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24'
                                        ) as e
                                        join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                                        where 
                                        month::date >= '{start_date}' and month::date <= '{end_date}'
                                        and LOWER("strip") <> '7x24'
                                        """
                
                

            if operating_day_flag:
                psql_query = f"""
                            {psql_query} and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                            """
                if not(query_strings["history"]):
                    psql_query_7x24 = f"""
                            {psql_query_7x24} and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                            """
                psql_query_7x24_hist = f"""
                            {psql_query_7x24_hist} and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}'
                            """
            # if 'cob' in query_strings:
            #     psql_query = f"""{psql_query} and cob='{query_strings['cob']}'"""
            #     psql_query_7x24 = f"""{psql_query_7x24} and cob='{query_strings['cob']}'"""
            #     psql_query_7x24_hist = f"""{psql_query_7x24_hist} and cob='{query_strings['cob']}'"""
            
            if normal_strip: # and not(query_strings["history"])
                psql_query_7x24 = psql_query_7x24+\
                            """ group by curvestart, curveend ,"month" ,control_area ,state ,load_zone ,capacity_zone ,utility ,cost_group ,cost_component ,sub_cost_component, r."7x24", e.distribution_category """
                psql_query_7x24_hist = psql_query_7x24_hist+\
                            """ group by curvestart, curveend ,"month" ,control_area ,state ,load_zone ,capacity_zone ,utility ,cost_group ,cost_component ,sub_cost_component, r."7x24", e.distribution_category """
                psql_query = psql_query + psql_query_7x24
                if query_strings["history"]:
                    psql_query = psql_query + psql_query_7x24_hist
            # end up the query
            psql_query =    f"""
                            {psql_query} order by curvestart desc,strip;
                            """
            data_frame = None
            data_frame = pd.read_sql_query(sql=text(psql_query), con=self.engine.connect())
            return data_frame, "success"  
        
        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
