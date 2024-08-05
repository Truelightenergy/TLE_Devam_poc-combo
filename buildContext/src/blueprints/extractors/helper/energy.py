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
            history = False
            cobonly = (query_strings["idcob"].lower() == 'cobonly')
            intradayonly  = (query_strings["idcob"].lower() == 'intradayonly')
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
                    select 'Distributed' "my_order",id, cob,  month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                    where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    UNION
                    select 'Distributed' "my_order",id, cob, month, curvestart, curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy_history
                    where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    
                """
                psql_query_7x24 = f"""
                    union all
                    select 'Normalized' "my_order",row_number() over () as id,cob ,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                    ROUND((sum(case
                    when e."strip" = '2x16' then e."data" * r."2x16"
                    when e."strip" = '5x16' then e."data" * r."5x16"
                    else e."data" * r."7x8"
                    end)/r."7x24")::numeric,2) as "data" ,
                    control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip" ,cost_group ,cost_component ,sub_cost_component
                    from trueprice.{control_area}_energy e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where 
                    month::date >= '{start_date}' and month::date <= '{end_date}' and e."strip" <> '7x24' curve_start_replace
                """
                psql_query_7x24_hist = f"""
                    UNION
                    select 'Normalized' "my_order",row_number() over () as id,cob ,"month" ,curvestart , curveend,
                    ROUND((sum(case
                    when e."strip" = '2x16' then e."data" * r."2x16"
                    when e."strip" = '5x16' then e."data" * r."5x16"
                    else e."data" * r."7x8"
                    end)/r."7x24")::numeric,2) as "data" ,
                    control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip" ,cost_group ,cost_component ,sub_cost_component
                    from trueprice.{control_area}_energy_history e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where 
                    month::date >= '{start_date}' and month::date <= '{end_date}' and e."strip" <> '7x24' curve_start_replace
                """
            else:
                psql_query = f"""
                    select 'Distributed' "my_order",id, cob, month, curvestart, TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend, data, control_area, state, load_zone, capacity_zone, utility, strip, cost_group, cost_component, sub_cost_component from trueprice.{control_area}_energy 
                    where {strip_query} month::date >= '{start_date}' and month::date <= '{end_date}' curve_start_replace
                    
                """
                psql_query_7x24 = f"""
                    union all
                    select 'Normalized' "my_order",row_number() over () as id,cob ,"month" ,curvestart , TO_TIMESTAMP('9999-12-31 23:59:59','YYYY-MM-DD HH24:MI:SS') as curveend,
                    ROUND((sum(case
                    when e."strip" = '2x16' then e."data" * r."2x16"
                    when e."strip" = '5x16' then e."data" * r."5x16"
                    else e."data" * r."7x8"
                    end)/r."7x24")::numeric,2) as "data" ,
                    control_area ,state ,load_zone ,capacity_zone ,utility , '7x24' "strip" ,cost_group ,cost_component ,sub_cost_component
                    from trueprice.{control_area}_energy e
                    join trueprice.monthly_reference_data r on to_char(e."month", 'YYYY-MM') = r."CalMonth" and r."ISO"='{control_area.upper()}'
                    where 
                    month::date >= '{start_date}' and month::date <= '{end_date}' and e."strip" <> '7x24' curve_start_replace
                """
            
            curve_start_replace = f"""  and curvestart::date >= '{curve_start}' and curvestart::date <= '{curve_end}' """
            psql_query = psql_query.replace('curve_start_replace', curve_start_replace)
            psql_query_7x24 = psql_query_7x24.replace('curve_start_replace', curve_start_replace)
            psql_query_7x24_hist = psql_query_7x24_hist.replace('curve_start_replace', curve_start_replace)
                
            if cobonly:
                psql_query = f"""{psql_query} and cob='{True}'"""
                psql_query_7x24 = f"""{psql_query_7x24} and cob='{True}'"""
            elif intradayonly:
                psql_query = f"""{psql_query} and cob='{False}'"""
                psql_query_7x24 = f"""{psql_query_7x24} and cob='{False}'"""
            if normal_strip:
                psql_query_7x24 = psql_query_7x24+\
                            """ group by cob ,curvestart, curveend ,"month" ,control_area ,state ,load_zone ,capacity_zone ,utility ,cost_group ,cost_component ,sub_cost_component, r."7x24" """
                psql_query_7x24_hist = psql_query_7x24_hist+\
                            """ group by cob ,curvestart, curveend ,"month" ,control_area ,state ,load_zone ,capacity_zone ,utility ,cost_group ,cost_component ,sub_cost_component, r."7x24" """
                psql_query = psql_query + psql_query_7x24
                if history:
                    psql_query = psql_query + psql_query_7x24_hist
            # end up the query
            psql_query =    f"""
                            {psql_query} order by curvestart desc, strip;
                            """
            data_frame = None
            data_frame = pd.read_sql_query(sql=psql_query, con=self.engine.connect())
            
            
            return data_frame, "success"  
            

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
