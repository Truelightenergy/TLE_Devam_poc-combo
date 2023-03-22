"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from .energy_ingestors.isone_energy import Isone_Energy
from .energy_ingestors.ercot_energy import Ercot_Energy
from .energy_ingestors.pjm_energy import Pjm_Energy
from .energy_ingestors.miso_energy import Miso_Energy
from .energy_ingestors.nyiso_energy import Nyiso_Energy

class Energy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        self.isone_ingestor = Isone_Energy()
        self.ercot_ingestor = Ercot_Energy()
        self.pjm_ingestor = Pjm_Energy()
        self.miso_ingestor = Miso_Energy()
        self.nyiso_ingestor = Nyiso_Energy()

    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """
        
        if data.controlArea == "nyiso":
            return self.nyiso_ingestor.ingestion(data)
        elif data.controlArea == "miso":
            return self.miso_ingestor.ingestion(data)
        elif data.controlArea == "ercot":
            return self.ercot_ingestor.ingestion(data)
        elif data.controlArea == "pjm":
            return self.pjm_ingestor.ingestion(data)
        elif data.controlArea == "isone":
            return self.isone_ingestor.ingestion(data)
        
        