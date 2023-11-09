"""
handles the operations of the garph veiw utility
"""

import plotly
import json
import pandas as pd
import plotly.io as pio
import plotly.express as px
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
    
    def get_email(self, token):
        """
        extracts the email from the token 
        """
        payload = self.db_model.decode_auth_token(token)[1]
        return payload["client_email"]