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