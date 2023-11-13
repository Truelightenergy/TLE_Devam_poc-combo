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


    def generate_line_chart(self, table, location, start_date, end_date,operating_day,history,cod,operatin_day_timestamp):

        """
        generates the line chart based on the available data
        """
        df = self.db_model.get_data(table, location, start_date, end_date,operating_day,history,cod,operatin_day_timestamp)
        pio.templates.default = "plotly_dark"
        
        fig = px.line(df, x = "month", y = "data", line_shape='linear')

        fig.update_traces(mode="markers+lines", hovertemplate=None)
        fig.update_layout(
        template="plotly_dark",  # Use dark theme
        title="Energy prices over time",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Energy",
        xaxis=dict(showgrid=False),
        hovermode="x unified",
        
        )
        line_color = "#1addc3"
        for trace in fig.data:
            trace.line.color = line_color

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    
    def generate_line_charts(self, parameters_array):
        """
        generates line charts for each set of parameters in the array
        """
        pio.templates.default = "plotly_dark"
        fig = go.Figure()


        for params in parameters_array:
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