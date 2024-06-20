import jwt
from utils.database_connection import ConnectDatabase

class ExtractorUtil:

    """
    creates the model of the admin operations
    """

    def __init__(self, secret_key, secret_salt):
        """
        connection database here 
        """

        self.secret_key = secret_key
        self.secret_salt = secret_salt
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def decode_auth_token(self, auth_token):
        """
        validate the Auth Token
        """
        try:
            response = jwt.decode(
                        auth_token, self.secret_key, algorithms=["HS256"])
            return True, response
        except:
            return False, None
        
    def fetch_latest_operating_day(self, table):
        """
        fetches the latest operating day from table
        """

        try:
            query = f"SELECT MAX(DATE(curvestart::date)) AS latest_date FROM trueprice.{table};"
            result = self.engine.execute(query)
            if result.rowcount >0:
                for row in result:
                    result = row
                    result = result[0].strftime('%Y-%m-%d')
                    break
                return result, 0
            return None, None
        except:
            return None, None
        
    def get_all_operating_days(self, curve, iso):
        """
        fetches the latest operating day from table
        """
        operating_days = []
        try:
            if curve.lower() == 'all':
                curve_list = ['energy', 'nonenergy', 'rec', 'ptc', 'matrix', 'headroom']
            else:
                curve_list = [curve.lower()]
            if iso == 'all':
                iso_list = ["ERCOT", "ISONE", "NYISO","MISO", "PJM"]
            else:
                iso_list = [iso]
            
            for curve in curve_list:
                if curve in ['energy', 'nonenergy', 'rec']:
                    for iso in iso_list:
                        if curve == 'rec' and iso.lower() == 'miso':
                            continue
                        table = f"{iso}_{curve}"
                        query = f"SELECT DISTINCT(DATE(curvestart::date)) AS latest_date FROM trueprice.{table};"
                        result = self.engine.execute(query)
                        if result.rowcount >0:
                            for row in result:
                                result = row
                                operating_days.append(result[0].strftime('%Y-%m-%d'))
                elif curve in ['ptc', 'matrix', 'headroom']:
                    table = curve
                    query = f"SELECT DISTINCT(DATE(curvestart::date)) AS latest_date FROM trueprice.{table}"
                    if iso != 'all':
                        query = query + f" WHERE control_area_type = '{iso}'"
                    query = query + ";"
                    result = self.engine.execute(query)
                    if result.rowcount >0:
                        for row in result:
                            result = row
                            operating_days.append(result[0].strftime('%Y-%m-%d'))
                else:
                    query = f"SELECT DISTINCT(DATE(curvestart::date)) AS latest_date FROM trueprice.loadprofile"
                    # if iso != 'all':
                    #     query = query + f" WHERE control_area_type = '{iso}'"
                    query = query + ";"
                    result = self.engine.execute(query)
                    if result.rowcount >0:
                        for row in result:
                            result = row
                            operating_days.append(result[0].strftime('%Y-%m-%d'))
        except:
            return operating_days
        return operating_days
        
    def get_all_operating_days_with_load_zone(self, table, load_zone):
        """
        fetches the latest operating day from table
        """
        operating_days = []
        query = f"SELECT DISTINCT(DATE(curvestart::date)) AS latest_date FROM trueprice.{table} WHERE load_zone = '{load_zone}';"
        
        try:
            operating_days = []
            result = self.engine.execute(query)
            if result.rowcount >0:
                for row in result:
                    result = row
                    operating_days.append(result[0].strftime('%Y-%m-%d'))
            return operating_days
        except:
            return operating_days
        
    def cob_availability(self, iso, sdate, edate):
        """
        availability check for cob
        """
        try:
            cob = False
            noncob = False
            if iso=='all':
                iso_list = ["isone", "pjm", "ercot", "nyiso", "miso"]
            else:
                iso_list = [iso]
            for iso in iso_list:
                query = f"SELECT * FROM trueprice.{iso}_energy where cob = {True} and curvestart::date>='{sdate}' and curvestart::date<='{edate}';"
                result = self.engine.execute(query)
                if result.rowcount >0:
                    cob =  True
                    break
            for iso in iso_list:
                query = f"SELECT * FROM trueprice.{iso}_energy where cob = {False} and curvestart::date>='{sdate}' and curvestart::date<='{edate}';"
                result = self.engine.execute(query)
                if result.rowcount >0:
                    noncob =  True
                    break
            return cob, noncob
        except:
            return False, False
    
    def intraday_timestamps_download(self, curve, iso, operating_day_start, operating_day_end):
        """
        extracts all the intraday timestamps and their history status from the database
        """
        try:
            timestamps = []
            if curve.lower() == 'all':
                curve_list = ['energy', 'nonenergy', 'rec', 'ptc', 'matrix', 'headroom']
            else:
                curve_list = [curve.lower()]
            if iso == 'all':
                iso_list = ["ERCOT", "ISONE", "NYISO","MISO", "PJM"]
            else:
                iso_list = [iso]
            
            for curve in curve_list:
                if curve in ['energy', 'nonenergy', 'rec']:
                    for iso in iso_list:
                        if curve == 'rec' and iso.lower() == 'miso':
                            continue
                        table = f"{iso}_{curve}"
                        query = f"""
                            SELECT distinct curvestart, false "cob" FROM trueprice.{table}_history 
                            WHERE curvestart::date >= '{operating_day_start}' and curvestart::date <= '{operating_day_end}'
                            UNION 
                            SELECT distinct curvestart, false "cob" FROM trueprice.{table} 
                            WHERE curvestart::date >= '{operating_day_start}' and curvestart::date <= '{operating_day_end}'
                            order by curvestart desc;
                        """
                        if curve == 'energy':
                            query = query.replace('false "cob"', 'cob')
                        results = self.engine.execute(query).fetchall()
                        timestamps.extend([{'timestamp': row['curvestart'].strftime('%Y-%m-%d %H:%M'),'cob':row['cob'], 'curve': table} for row in results])
                else:
                    table = curve
                    # Will add "strip='7x24'" in query just to replace with strings below else its not necessary
                    query = f"""
                        SELECT distinct curvestart, false "cob" FROM trueprice.{table}_history 
                        WHERE curvestart::date >= '{operating_day_start}' and curvestart::date <= '{operating_day_end}' AND strip='7x24'
                        UNION 
                        SELECT distinct curvestart, false "cob" FROM trueprice.{table} 
                        WHERE curvestart::date >= '{operating_day_start}' and curvestart::date <= '{operating_day_end}' AND strip='7x24'
                        order by curvestart desc
                    """
                    if iso != 'all':
                        query = query.replace("AND strip='7x24'", f" and control_area_type = '{iso}'")
                    else:
                        query = query.replace("AND strip='7x24'", '')
                    query = query + ";"
                    results = self.engine.execute(query).fetchall()
                    timestamps.extend([{'timestamp': row['curvestart'].strftime('%Y-%m-%d %H:%M'),'cob':row['cob'], 'curve': table} for row in results])
            return timestamps
        except:
            return []