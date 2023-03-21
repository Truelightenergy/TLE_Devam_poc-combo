"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from .ancillarydatadetails_ingestors.isone_ancillarydatadetails import Isone_AncillaryDataDetails


class AncillaryDataDetails:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the constructors
        """
        self.isone_ingestor = Isone_AncillaryDataDetails()
        
    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """

        if data.controlArea == "isone":
            return self.isone_ingestor.ingestion(data)
