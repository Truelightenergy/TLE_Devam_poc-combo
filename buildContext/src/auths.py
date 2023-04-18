"""
Managing Authentications and Autherizations
"""
import jwt
import datetime
import hashlib
from database_conection import ConnectDatabase

class Auths:
    """
    Managing Authentications and Autherizations
    """

    def __init__(self, secret_key):
        """
        connection database here 
        """

        self.secret_key =secret_key
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def create_user(self, client_email, client_password, isAdmin):
        """
        creating a new user for now
        """

        client_password = hashlib.sha256(client_password.encode()).digest().hex()
        query = f"INSERT INTO trueprice.users(email, password, isadmin)VALUES ('{client_email}', '{client_password}', {isAdmin});"
        try:
            self.engine.execute(query)
            return True
        except :
            return False
            
    def authenticate_user(self, client_email, client_password):
        """
        authenticate user based on given cradentials
        """
        client_password = hashlib.sha256(client_password.encode()).digest().hex()
        query = f"SELECT * FROM trueprice.users WHERE email = '{client_email}' AND password = '{client_password}';"

        try:
            results = self.engine.execute(query).fetchall()
            flag = False
            admin_check = False
            for row in results:
                flag = True
                admin_check = row['isadmin']
            return flag, admin_check
        except:
            return False, False
        
    def change_password(self, email, new_password):
        """
        allowing user to change his password
        """
        query = f"UPDATE trueprice.users SET password = '{new_password}' WHERE email = '{email}'";
    
        try:
            self.engine.execute(query)
            return True
        except:
            return False
          
    def encode_auth_token(self, client_email, client_password):
        """
        Generates the Auth Token
        
        """
        client_password = hashlib.sha256(client_password.encode()).digest().hex()
        try:
            token = jwt.encode({'client_email' : client_email, 
                                'client_password' : client_password,
                        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=1)},
                        self.secret_key, "HS256")
            return True, token
        except:
            return False, None
    
        
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
