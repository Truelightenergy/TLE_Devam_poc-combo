"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from .rec_ingestors.pjm_rec import Pjm_Rec
from .rec_ingestors.ercot_rec import Ercot_Rec
from .rec_ingestors.isone_rec import Isone_Rec
from .rec_ingestors.nyiso_rec import Nyiso_Rec

class Rec:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the constructors
        """
        self.pjm_ingestor = Pjm_Rec()
        self.ercot_ingestor = Ercot_Rec()
        self.isone_ingestor = Isone_Rec()
        self.nyiso_ingestor = Nyiso_Rec()
        
    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """

        if data.controlArea == "pjm":
            return self.pjm_ingestor.ingestion(data)
        elif data.controlArea == "ercot":
            return self.ercot_ingestor.ingestion(data)
        elif data.controlArea == "isone":
            return self.isone_ingestor.ingestion(data)
        elif data.controlArea == "nyiso":
            return self.nyiso_ingestor.ingestion(data)
        
