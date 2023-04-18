"""
Implements the Extraction of Forward Curve Data from the database
"""

import pandas as pd
from datetime import datetime
from database_conection import ConnectDatabase


class Energy:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the connection with database
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def extraction(self, query_strings):
        """
        Handling extraction for ancillarydata
        """
        try:
            control_area = query_strings["iso"]
            strip = query_strings["strip"]
            start_date_stamp = query_strings["start"]
            end_date_stamp = query_strings["end"]

            start_date = str(datetime.strptime(start_date_stamp, "%Y%m%d").date())
            end_date = str(datetime.strptime(end_date_stamp, "%Y%m%d").date())
            

            if control_area == "nyiso" or control_area == "miso" or control_area == "ercot" or control_area == "pjm" or control_area == "isone":
                data_frame = None
                psql_query = f"select * from trueprice.{control_area}_energy where LOWER(strip) = '{strip.lower()}' and month::date >= '{start_date}' and month::date <= '{end_date}';"
                print(psql_query)
                data_frame = pd.read_sql_query(sql=psql_query, con=self.engine.connect())
                return data_frame, "success"  
            else:
                return None, "Unable to Fetch Results"

        except:
            import traceback, sys
            print(traceback.format_exc())
            return None, traceback.format_exc()
