"""
handles the operations of the garph veiw utility
"""

import plotly
import json
import pandas as pd
import plotly.io as pio
import plotly.graph_objs as go
import plotly.express as px
import random
from .graphview_model import GraphView_Util
from datetime import datetime, timedelta
from utils.configs import read_config
from ..extractors.helper.extraction_rules import Rules
from flask import session


config = read_config()
class Util:
    """
    handles the operations of the garph view utility
    """

    def __init__(self):
        """
        loads the models
        """

        secret_key = config['secret_key']
        secret_salt = config['secret_salt']
        self.db_model = GraphView_Util(secret_key, secret_salt)
        self.filter = Rules()

    def generate_random_color(self):
        """Generate a random HTML color code favoring a primary color."""
        # Choose which primary color to emphasize
        primary = random.choice(['r', 'g', 'b'])

        # Depending on the choice, make one color component dominant
        if primary == 'r':
            r = random.randint(128, 255)
            g = random.randint(0, 127)
            b = random.randint(0, 127)
        elif primary == 'g':
            r = random.randint(0, 127)
            g = random.randint(128, 255)
            b = random.randint(0, 127)
        else:  # primary == 'b'
            r = random.randint(0, 127)
            g = random.randint(0, 127)
            b = random.randint(128, 255)

        # Combine the components into a single string and return it
        return '#{:02X}{:02X}{:02X}'.format(r, g, b)


    def generate_line_chart(self, tables, locations, start_dates, end_dates,operating_days,historys,cods,operatin_day_timestamps):

        """
        generates the line chart based on the available data
        """
        dataframes = []
       
        for i, (table, location, start_date, end_date, operating_day, history, cod, operatin_day_timestamp) \
            in enumerate(zip(tables,locations, start_dates, end_dates, operating_days, historys,cods,operatin_day_timestamps)):

            df = self.db_model.get_data(table, location, start_date, end_date, operating_day, history, cod, operatin_day_timestamp) 
            dataframes.append(df)
        
        combined_df = pd.concat([df.assign(source=i) for i, df in enumerate(dataframes)], keys=range(len(dataframes)))

            
        pio.templates.default = "plotly_dark"
        fig = px.line(combined_df, x='month', y='data', color='source', line_group='source',
              labels={'source': 'DataFrame Index'})
        fig.update_traces(mode="markers+lines", hovertemplate=None)


        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    
    def fetch_data(self, params):
        """
        fetches data from the database
        """

        df = self.db_model.get_data(
                                        params['control_table'],
                                        params['loadZone'],
                                        params['start'],
                                        params['end'],
                                        params['operating_day'],
                                        params['history'],
                                        params['cob'],
                                        params['operatin_day_timestamps']
                                        )
        return df
    
    def calculate_balanced_month(self, months):
        current_date = datetime.now()
        first_day_of_month = current_date.replace(day=1)
        end_date = first_day_of_month + timedelta(days=months * 30)
        end_date = end_date.replace(day=1)

        first_day_of_month = first_day_of_month.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        start_date = pd.to_datetime(first_day_of_month, utc=True)
        end_date = pd.to_datetime(end_date, utc=True)

        return start_date.date(), end_date.date()
    
    def dataframe_filtering(self, dataframe, rules, control_table):
        """
        filter the data based on the user subscription rules
        """
        dataframes = []
        for row in rules:
            if ("headroom" in control_table) or ("ptc" in control_table):
                query = f"control_area == '{row['control_area']}' & state == '{row['state']}' & load_zone == '{row['load_zone']}' & capacity_zone == '{row['capacity_zone']}' & utility == '{row['utility']}' & strip == '{row['strip']}' & cost_group == '{row['cost_group']}' & cost_component == '{row['cost_component']}'"
            else:
                query = f"control_area == '{row['control_area']}' & state == '{row['state']}' & load_zone == '{row['load_zone']}' & capacity_zone == '{row['capacity_zone']}' & utility == '{row['utility']}' & strip == '{row['strip']}' & cost_group == '{row['cost_group']}' & cost_component == '{row['cost_component']}' & sub_cost_component == '{row['sub_cost_component']}'"
            df = dataframe.query(query)
            if (("headroom" in control_table) or ("ptc" in control_table) or ("matrix" in control_table)):
                pass
            else: 
                if row['balanced_month_range'] ==  0:
                    df = df.loc[(df['month'] >= row['startmonth']) & (df['month'] <= row['endmonth'])]
                else:
                    start_month, end_month = self.calculate_balanced_month(row['balanced_month_range'])
                    df = df.loc[(df['month'] >= start_month) & (df['month'] <= end_month)]
            dataframes.append(df)
        if len(dataframes)>=1:    
            return pd.concat(dataframes, axis=0), "success"
        return None, "error"
    
    def generate_line_charts(self, parameters_array):
        """
        generates line charts for each set of parameters in the array
        """
        # pio.templates.default = "plotly"
        # fig = go.Figure()
        fig = []
        hours = []
        for i, params in enumerate(parameters_array):
            if i>0:
                try:
                    datetime_object = datetime.strptime(params['operatin_day_timestamps'], '%Y-%m-%d %H:%M')
                except:
                    datetime_object = datetime.strptime(params['operatin_day_timestamps'], '%Y-%m-%d')
                date_only_string = datetime_object.strftime('%Y-%m-%d')

                params['operatin_day_timestamps'] = date_only_string
            df = self.fetch_data(params)
            if df.empty:
                cob_flag =  params['cob']
                if params['cob']== False or params['cob']=='false':
                    params['cob'] = True
                    df = self.fetch_data(params)
                elif params['cob']== True or params['cob']=='true':
                    params['cob'] = False
                    df = self.fetch_data(params)
            if df.empty:
                if params['history']== False or params['history']=='false':
                    params['history'] = True
                    params['cob'] = cob_flag
                    df = self.fetch_data(params)
                elif params['history']== True or params['history']=='true':
                    params['history'] = False
                    params['cob'] = cob_flag
                    df = self.fetch_data(params)
            email = session["user"]
            if session["level"]!= 'admin':
                rules = self.filter.filter_data(params['control_table'], email)
                df, status = self.dataframe_filtering(df, rules, params['control_table'])
            if (session["level"]== 'admin')or(status !='error'):

                if i==0 :
                    color = 'rgb(0,90,154)'
                    markerColor = 'rgb(240,192,85)'
                elif i==1:
                    color = 'rgb(240,192,85)'
                    markerColor = 'rgb(0,90,154)'
                else: 
                    color = self.generate_random_color()
                    markerColor = self.generate_random_color()
                                

                update = 'ID'
                if params['cob']== True or params['cob']=='true':
                    update = 'COB'
                # df = self.db_model.get_data(**params)  # Unpacking parameters for the get_data method
                label =params["control_table"].split('_')[0].upper() + " " + params.get("label", f"{params['loadZone']}: {params['operatin_day_timestamps']} {update}")
                fig.append(dict(
                    x=list(df["month"].astype(str)), 
                    y=list(df["data"]), 
                    mode="markers+lines",
                    name=label,  # You can pass a label for each line
                    showlegend=True,
                    line=dict(
                        shape='spline',  
                        color=color,  
                        width=4  
                    ),
                    marker=dict(
                        size=8,  
                        color=markerColor,  
                        line=dict(
                            color=markerColor,
                            width=2  
                        )
                    )))
                hours.append(list(df["7x24"]))
        graphJSON = json.dumps({'data':fig, 'hours': hours})
        return graphJSON

    def validate_access(self, rules, control_table, load_zone):
        """
        check availability of access to current user
        """
        flag = False
        for rule in rules:
            if (rule['control_table'] == control_table) and (rule['load_zone']== load_zone) and (rule['strip']=='5x16'):
                flag = True
                break
        return flag
    
    def generate_graph_view_for_home_screen(self, notification_params, operating_day, operating_day_ts, prev_day, start, end):
        """
        creates the graphview based on the raw parameters
        """
        params = list()
        for raw_params in notification_params:
            control_table = ((raw_params.split(',')[0]).split('in')[-1]).strip()
            load_zone = ((raw_params.split(',')[1]).split('(5x16)')[0]).strip()
            email = session["user"]
            if session["level"]!= 'admin':
                rules = self.filter.filter_data(f'{control_table.lower()}_energy', email)
                access_flag = self.validate_access(rules, f'{control_table.lower()}_energy', load_zone)
                if not access_flag:
                    continue


            previous_day = self.db_model.get_previous_day(load_zone, control_table)
            if previous_day is not None:
                prev_day = previous_day.strftime('%Y-%m-%d')

            params= [{'data_type': 'Energy', 'control_table': f'{control_table.lower()}_energy', 'loadZone': load_zone, 'operating_day': operating_day, 'operatin_day_timestamps': operating_day_ts, 'history': 'false', 'cob': 'false', 'start': start, 'end': end}, 
            {'data_type': 'Energy', 'control_table': f'{control_table.lower()}_energy', 'loadZone': load_zone, 'operating_day': prev_day, 'operatin_day_timestamps': prev_day, 'history': 'false', 'cob': 'false', 'start': start, 'end': end}]
        
            if (session["level"] == 'admin') or access_flag:
                break

        graph = self.generate_line_charts(params)
        
        return graph, params

    def get_email(self, token):
        """
        extracts the email from the token 
        """
        payload = self.db_model.decode_auth_token(token)[1]
        return payload["client_email"]
    
    def get_graphs(self, garph_id):
        """
        generates the graph based on the graph id
        """

        return self.db_model.get_graph_data(garph_id)
    
    def get_graphs(self, garph_id):
        """
        generates the graph based on the graph id
        """

        return self.db_model.get_graph_data(garph_id)
    
    
    
