"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from .ancillarydata_ingestors.isone_ancillarydata import Isone_AncillaryData
from .ancillarydata_ingestors.ercot_ancillarydata import Ercot_AncillaryData


class AncillaryData:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the constructors
        """
        self.isone_ingestor = Isone_AncillaryData()
        self.ercot_ingestor = Ercot_AncillaryData()
        
    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """
        if data.controlArea == "isone":
            return self.isone_ingestor.ingestion(data)
        elif data.controlArea == "ercot":
            return self.ercot_ingestor.ingestion(data)

