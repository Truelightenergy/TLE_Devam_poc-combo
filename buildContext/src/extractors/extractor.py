"""
makes query to the database and returns to the database
"""

import pandas as pd
from .database_conection import ConnectDatabase
from .ancillarydata import AncillaryData
from .ancillarydatadetails import AncillaryDataDetails
from .energy import ForwardCurve

class Extractor:
    """
    class which expects filters to get data from the db and return in pandas
    """
    def __init__(self):
        """
        database connection will be loaded here
        """

        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

        self.ancillary_data = AncillaryData()
        self.anciallary_data_details = AncillaryDataDetails()
        self.forward_curve = ForwardCurve()

    def get_custom_data(self, query_strings):
        """
        extracts the data from the database based on the query strings
        """
        dataframe = None
        status = "Unable to Fetch Data"
        if query_strings["curve_type"] == "ancillarydata":
            dataframe, status = self.ancillary_data.extraction(query_strings)
        elif query_strings["curve_type"] == "ancillarydatadetails":
            dataframe, status = self.anciallary_data_details.extraction(query_strings)
        elif query_strings["curve_type"] == "forwardcurve":
            dataframe, status = self.forward_curve.extraction(query_strings)
            
        return dataframe, status

            # http://127.0.0.1:5555/get_data?start=20230101&end=20230102&iso=isone&strip=24x7&curve_type=ancillarydata&type=csv
            # http://127.0.0.1:5555/get_data?start=20230101&end=20230109&iso=isone&strip=7x8&curve_type=forwardcurve&type=csv
        

