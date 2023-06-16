import jwt
from utils.database_connection import ConnectDatabase

class IngestorUtil:

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

    def save_log(self,time_stamp, email, filename):
        """
        make a log for uploaded file
        """
        try:
            query = f"INSERT INTO trueprice.uploads(timestamp, email, filename) VALUES ('{time_stamp}', '{email}', '{filename}');"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
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