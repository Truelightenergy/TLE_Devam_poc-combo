"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from .matrix_ingestors.matrix import MATRIX

class Ptc:
    """
    constructor which will makes the connection to the database
    """
    def __init__(self):
        """
        makes the constructors
        """
        self.matrix_ingestor = MATRIX()

    def ingestion(self, data):
        """
        Handling Ingestion for matrix
        """
        return self.matrix_ingestor.ingestion(data)