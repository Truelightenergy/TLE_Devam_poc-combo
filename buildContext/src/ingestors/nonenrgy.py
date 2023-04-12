"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

from .nonenergy_ingestors.isone_nonenergy import Isone_NonEnergy
# from .nonenergy_ingestors.ercot_nonenergy import Ercot_NonEnergy


class NonEnergy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the constructors
        """
        self.isone_ingestor = Isone_NonEnergy()
        # self.ercot_ingestor = Ercot_NonEnergy()
        
    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """

        if data.controlArea == "isone":
            return self.isone_ingestor.ingestion(data)
        # elif data.controlArea == "ercot":
        #     return self.ercot_ingestor.ingestion(data)
