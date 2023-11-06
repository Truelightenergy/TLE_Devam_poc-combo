"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from .ptc_ingestors.ptc import PTC

class Ptc:
    """
    constructor which will makes the connection to the database
    """
    def __init__(self):
        """
        makes the constructors
        """
        self.ptc_ingestor = PTC()

    def ingestion(self, data):
        """
        Handling Ingestion for ptc
        """
        return self.ptc_ingestor.ingestion(data)