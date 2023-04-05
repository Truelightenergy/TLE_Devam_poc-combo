"""
makes query to the database and returns to the database
"""

import pandas as pd
from .database_conection import ConnectDatabase
from .nonenergy import NonEnergy
from .energy import Energy
from .rec import Rec

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

        self.non_energy = NonEnergy()
        self.energy = Energy()
        self.rec= Rec()

    def get_custom_data(self, query_strings):
        """
        extracts the data from the database based on the query strings
        """
        dataframe = None
        status = "Unable to Fetch Data"
        if query_strings["curve_type"] == "nonenergy":
            dataframe, status = self.non_energy.extraction(query_strings)
        elif query_strings["curve_type"] == "energy":
            dataframe, status = self.energy.extraction(query_strings)
        elif query_strings["curve_type"] == "rec":
            dataframe, status = self.rec.extraction(query_strings)
            
        return dataframe, status

            # http://127.0.0.1:5555/get_data?start=20230101&end=20230102&iso=isone&strip=24x7&curve_type=ancillarydata&type=csv
            # http://127.0.0.1:5555/get_data?start=20230101&end=20230109&iso=isone&strip=7x8&curve_type=forwardcurve&type=csv
        

