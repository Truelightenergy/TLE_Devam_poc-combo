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
from datetime import datetime



class Util:
    """
    handles the operations of the garph view utility
    """

    def __init__(self):
        """
        loads the models
        """

        secret_key = "super-scret-key"
        secret_salt = "secret-salt"
        self.db_model = GraphView_Util(secret_key, secret_salt)

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
    
    def generate_line_charts(self, parameters_array):
        """
        generates line charts for each set of parameters in the array
        """
        pio.templates.default = "plotly_dark"
        fig = go.Figure()


        for i, params in enumerate(parameters_array):
            if i>0:
                datetime_object = datetime.strptime(params['operatin_day_timestamps'], '%Y-%m-%d %H:%M')
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
                

                
                
                

            
            color = self.generate_random_color()

            # df = self.db_model.get_data(**params)  # Unpacking parameters for the get_data method
            fig.add_trace(go.Scatter(
                x=df["month"], 
                y=df["data"], 
                mode="markers+lines",
                name=params.get("label", f"{params['loadZone']}: {params['operating_day']}"),  # You can pass a label for each line
                line_shape='linear',
                line=dict(color=color),  # Set the line color here if it's the same for all
            ))

        fig.update_layout(
            template="plotly_dark",
            title="Energy prices over time",
            title_x=0.5,
            xaxis_title="Date",
            yaxis_title="Energy",
            xaxis=dict(showgrid=False),
            hovermode="x unified",
        )

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

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