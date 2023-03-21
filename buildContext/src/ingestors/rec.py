"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from .rec_ingestors.pjm_rec import Pjm_RecData

class RecData:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the constructors
        """
        self.pjm_ingestor = Pjm_RecData()
        
    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """

        if data.controlArea == "pjm":
            return self.pjm_ingestor.ingestion(data)
