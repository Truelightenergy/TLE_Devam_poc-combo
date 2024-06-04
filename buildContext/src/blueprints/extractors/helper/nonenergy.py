"""
Implements the Extraction of non energy details from the database
"""

import pandas as pd
from datetime import datetime
from utils.database_connection import ConnectDatabase
from sqlalchemy import text
import re


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

    def replace_or_append(self, pattern, replacement, text):
        result = re.sub(pattern, replacement, text)
        if result == text:
            result += ' ($/'+replacement+')'
        return result

    def extraction(self, query_strings):
        """
        Handling extraction for ancillarydata
        """
        try:
            history = False
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
            
            elif history:
                psql_query = f"""
                    select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                    ROUND((case
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'reactive supply value%|teac%|nits rate%|arr credit%|ros%|lhv%|nyc%'
                    then (data/r."7x24")*1000
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'capacity price%'
                    then (data/24)*1000
                    when LOWER("strip") = '7x24' and  LOWER(cost_component) SIMILAR TO 'black start charge%|nits schedule 9%|arrs%'
                    then (data/r."7x24")
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'capacity charge%|capacity'
                    then ((data/r."7x24")*1000) * coalesce( (select data from trueprice.{control_area}_nonenergy s 
                    where s.curvestart=e.curvestart and s."month"=e."month" 
                    and s.control_area=e.control_area and s.state=e.state and s.load_zone=e.load_zone 
                    and s.capacity_zone=e.capacity_zone  and s.utility=e.utility --and s.cost_group=e.cost_group 
                    and lower(s.cost_component) in ('capacity scaling factor', 'capacity scaler') --and s.sub_cost_component=e.sub_cost_component
                    limit 1), 1)
                    else data
                    end)::numeric, 2) as "data", 
                    control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                    from trueprice.{control_area}_nonenergy e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    and lower(e.cost_component)<>'capacity scaling factor' and lower(e.cost_component)<>'capacity scaler'
                    UNION
                    select 'Distributed' "my_order",id, month, curvestart, curveend, 
                    ROUND((case
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'reactive supply value%|teac%|nits rate%|arr credit%|ros%|lhv%|nyc%'
                    then (data/r."7x24")*1000
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'capacity price%'
                    then (data/24)*1000
                    when LOWER("strip") = '7x24' and  LOWER(cost_component) SIMILAR TO 'black start charge%|nits schedule 9%|arrs%'
                    then (data/r."7x24")
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'capacity charge%|capacity'
                    then ((data/r."7x24")*1000) * coalesce( (select data from trueprice.{control_area}_nonenergy s 
                    where s.curvestart=e.curvestart and s."month"=e."month" 
                    and s.control_area=e.control_area and s.state=e.state and s.load_zone=e.load_zone 
                    and s.capacity_zone=e.capacity_zone  and s.utility=e.utility --and s.cost_group=e.cost_group 
                    and lower(s.cost_component) in ('capacity scaling factor', 'capacity scaler') --and s.sub_cost_component=e.sub_cost_component
                    limit 1), 1)
                    else data
                    end)::numeric, 2) as "data", 
                    control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                    from trueprice.{control_area}_nonenergy_history e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    and lower(e.cost_component)<>'capacity scaling factor' and lower(e.cost_component)<>'capacity scaler'
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
                    when LOWER(e.cost_component) like '%on%peak%' then e."data" * r."OnPeak"
                    when LOWER(e.cost_component) like '%off%peak%' then e."data" * r."OffPeak"
                    end)/r."7x24")::numeric,2) as "data" ,
                    control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,
                    replace(replace(replace(replace(replace(replace( LOWER(cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') "cost_component",
                    replace(replace(replace(replace(replace(replace( LOWER(sub_cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') "sub_cost_component"
                    from 
                    (
                    select 
                    case 
                    when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                    when LOWER("strip") in ('wd', 'we') then 'wd' 
                    else 'ph' 
                    end as distribution_category, 
                    * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24' or (LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO '%off%peak%|%on%peak%' )
                    ) as e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where 
                    month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    and (LOWER("strip") <> '7x24' or ( LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO '%off%peak%|%on%peak%' ) )
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
                    when LOWER(e.cost_component) like '%on%peak%' then e."data" * r."OnPeak"
                    when LOWER(e.cost_component) like '%off%peak%' then e."data" * r."OffPeak"
                    end)/r."7x24")::numeric,2) as "data" ,
                    control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,
                    replace(replace(replace(replace(replace(replace( LOWER(cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') "cost_component",
                    replace(replace(replace(replace(replace(replace( LOWER(sub_cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') "sub_cost_component"
                    from 
                    (
                    select 
                    case 
                    when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                    when LOWER("strip") in ('wd', 'we') then 'wd' 
                    else 'ph' 
                    end as distribution_category, 
                    * from trueprice.{control_area}_nonenergy_history where LOWER("strip") <> '7x24' or (LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO '%off%peak%|%on%peak%' )
                    ) as e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where 
                    month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    and (LOWER("strip") <> '7x24' or ( LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO '%off%peak%|%on%peak%' ) )
                    """
            else:
                psql_query = f"""
                    select 'Distributed' "my_order",id, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, 
                    ROUND((case
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'reactive supply value%|teac%|nits rate%|arr credit%|ros%|lhv%|nyc%'
                    then (data/r."7x24")*1000
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'capacity price%'
                    then (data/24)*1000
                    when LOWER("strip") = '7x24' and  LOWER(cost_component) SIMILAR TO 'black start charge%|nits schedule 9%|arrs%'
                    then (data/r."7x24")
                    when LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO 'capacity charge%|capacity'
                    then ((data/r."7x24")*1000) * coalesce( (select data from trueprice.{control_area}_nonenergy s 
                    where s.curvestart=e.curvestart and s."month"=e."month" 
                    and s.control_area=e.control_area and s.state=e.state and s.load_zone=e.load_zone 
                    and s.capacity_zone=e.capacity_zone  and s.utility=e.utility --and s.cost_group=e.cost_group 
                    and lower(s.cost_component) in ('capacity scaling factor', 'capacity scaler') --and s.sub_cost_component=e.sub_cost_component
                    limit 1), 1)
                    else data
                    end)::numeric, 2) as "data", 
                    control_area, state, load_zone, capacity_zone, utility, strip, '' "distribution_category", cost_group, cost_component, sub_cost_component 
                    from trueprice.{control_area}_nonenergy e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    and lower(e.cost_component)<>'capacity scaling factor' and lower(e.cost_component)<>'capacity scaler'
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
                    when LOWER(e.cost_component) like '%on%peak%' then e."data" * r."OnPeak"
                    when LOWER(e.cost_component) like '%off%peak%' then e."data" * r."OffPeak"
                    end)/r."7x24")::numeric,2) as "data" ,
                    control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip", e.distribution_category ,cost_group ,
                    replace(replace(replace(replace(replace(replace( LOWER(cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') "cost_component",
                    replace(replace(replace(replace(replace(replace( LOWER(sub_cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') "sub_cost_component" 
                    from 
                    (
                    select 
                    case 
                    when LOWER("strip") in ('2x16', '5x16', '7x8') then 'wdph' 
                    when LOWER("strip") in ('wd', 'we') then 'wd' 
                    else 'ph' 
                    end as distribution_category, 
                    * from trueprice.{control_area}_nonenergy where LOWER("strip") <> '7x24' or (LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO '%off%peak%|%on%peak%' )
                    ) as e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where 
                    month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    and (LOWER("strip") <> '7x24' or ( LOWER("strip") = '7x24' and LOWER(cost_component) SIMILAR TO '%off%peak%|%on%peak%' ) )
                    """
            
            curve_start_replace = f"""  and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}' """
            psql_query = psql_query.replace('curve_start_replace', curve_start_replace)
            psql_query_7x24 = psql_query_7x24.replace('curve_start_replace', curve_start_replace)
            psql_query_7x24_hist = psql_query_7x24_hist.replace('curve_start_replace', curve_start_replace)
            
            if normal_strip:
                psql_query_7x24 = psql_query_7x24+\
                            """ group by curvestart, curveend ,"month" ,control_area ,state ,load_zone ,capacity_zone ,utility ,cost_group ,
                            replace(replace(replace(replace(replace(replace( LOWER(cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') ,
                            replace(replace(replace(replace(replace(replace( LOWER(sub_cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') ,
                            r."7x24", e.distribution_category """
                psql_query_7x24_hist = psql_query_7x24_hist+\
                            """ group by curvestart, curveend ,"month" ,control_area ,state ,load_zone ,capacity_zone ,utility ,cost_group ,
                            replace(replace(replace(replace(replace(replace( LOWER(cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') ,
                            replace(replace(replace(replace(replace(replace( LOWER(sub_cost_component), 'on-peak',''), 'onpeak',''), 'on peak',''), 'off-peak',''), 'offpeak',''), 'off peak','') ,
                            r."7x24", e.distribution_category """
                psql_query = psql_query + psql_query_7x24
                if history:
                    psql_query = psql_query + psql_query_7x24_hist
            # end up the query
            psql_query =    f"""
                            {psql_query} order by curvestart desc,strip;
                            """
            data_frame = None
            data_frame = pd.read_sql_query(sql=text(psql_query), con=self.engine.connect())
            data_frame.cost_component = data_frame.cost_component.apply(lambda x: self.replace_or_append(r'[KkMmWw]{2}[\-/ ]{0,1}[MmOoNnTtHhDdAaYyHhOoUuRr]{1,5}', 'MWh', x))
            data_frame.sub_cost_component = data_frame.sub_cost_component.apply(lambda x: re.sub(r'[KkMmWw]{2}[\-/ ]{0,1}[MmOoNnTtHhDdAaYyHhOoUuRr]{1,5}', 'MWh', x))
            return data_frame, "success"
        
        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
