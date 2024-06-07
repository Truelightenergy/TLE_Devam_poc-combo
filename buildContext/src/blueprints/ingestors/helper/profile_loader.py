"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
from ..ingestor_model import IngestorUtil
from utils.configs import read_config

config = read_config()

class Profile_Loader:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        self.secret_key = config['secret_key']
        self.secret_salt = config['secret_salt']
        self.db_util = IngestorUtil(self.secret_key, self.secret_salt)

    def ingestion(self, data):
        """
        Handling Ingestion for ancillarydata
        """
        return None
    