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

    def generate_line_chart(self, tables, locations, start_dates, end_dates, operating_days, historys, cods, operatin_day_timestamps):

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