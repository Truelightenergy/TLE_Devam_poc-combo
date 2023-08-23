"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from ..ingestor_model import IngestorUtil
from .energy_ingestors.isone_energy import Isone_energy
from .energy_ingestors.ercot_energy import Ercot_energy
from .energy_ingestors.pjm_energy import Pjm_energy
from .energy_ingestors.miso_energy import Miso_energy
from .energy_ingestors.nyiso_energy import Nyiso_energy

class Energy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        self.secret_key = "super-scret-key" #env variable
        self.secret_salt = "secret-salt" #env variable
        self.db_util = IngestorUtil(self.secret_key, self.secret_salt)

        self.isone_ingestor = Isone_energy()
        self.ercot_ingestor = Ercot_energy()
        self.pjm_ingestor = Pjm_energy()
        self.miso_ingestor = Miso_energy()
        self.nyiso_ingestor = Nyiso_energy()

    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """
        
        if data.controlArea == "nyiso":
            result = self.nyiso_ingestor.ingestion(data)
        elif data.controlArea == "miso":
            result = self.miso_ingestor.ingestion(data)
        elif data.controlArea == "ercot":
            result = self.ercot_ingestor.ingestion(data)
        elif data.controlArea == "pjm":
            result = self.pjm_ingestor.ingestion(data)
        elif data.controlArea == "isone":
            result = self.isone_ingestor.ingestion(data)
        
        if "data inserted" in result.lower():
            # logging the trigger
            self.db_util.event_for_notification(data.curveStart, data.controlArea+"_energy")
        return result