"""
Implements the Slowly Changed Dimensions to insert the data into database
"""
import datetime
import pandas as pd
from .forwardcurve_ingestors.isone__forwardcurve import Isone_ForwardCurve
from .forwardcurve_ingestors.ercot_forwardcurve import Ercot_ForwardCurve
from .forwardcurve_ingestors.pjm__forwardcurve import Pjm_ForwardCurve
from .forwardcurve_ingestors.miso_forwardcurve import Miso_ForwardCurve
from .forwardcurve_ingestors.nyiso_forwardcurve import Nyiso_ForwardCurve

class ForwardCurve:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        self.isone_ingestor = Isone_ForwardCurve()
        self.ercot_ingestor = Ercot_ForwardCurve()
        self.pjm_ingestor = Pjm_ForwardCurve()
        self.miso_ingestor = Miso_ForwardCurve()
        self.nyiso_ingestor = Nyiso_ForwardCurve()

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
        
        