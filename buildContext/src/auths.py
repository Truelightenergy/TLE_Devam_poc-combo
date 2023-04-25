"""
Managing Authentications and Autherizations
"""
import jwt
import datetime
import hashlib
from database_connection import ConnectDatabase

class Auths:
    """
    Managing Authentications and Authorizations
    """

    def __init__(self, secret_key, secret_salt):
        """
        connection database here 
        """

        self.secret_key = secret_key
        self.secret_salt = secret_salt
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def create_user(self, client_email, client_password, level):
        """
        creating a new user for now
        """

        salted_password = self.secret_salt + client_password 
        hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
        query = f"INSERT INTO trueprice.users(email, password, privileged_level) VALUES ('{client_email}', '{hashed_salted_password}', '{level}');"
        
        try:
            self.engine.execute(query)
            return True
        except :
            return False
            
    def authenticate_user(self, client_email, client_password):
        """
        authenticate user based on given credentials
        """
        salted_password = self.secret_salt + client_password 
        hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
        query = f"SELECT * FROM trueprice.users WHERE email = '{client_email}' AND password = '{hashed_salted_password}';"

        try:
            results = self.engine.execute(query).fetchall()
            flag = False
            admin_check = False
            for row in results:
                flag = True
                admin_check = row['privileged_level']
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
        salted_password = self.secret_salt + client_password 
        hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
        try:
            token = jwt.encode({'client_email' : client_email, 
                                'client_password' : hashed_salted_password,
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
        
    def get_all_users(self):
        """
        extracts all the users from the database
        """
        query = f"SELECT * FROM trueprice.users;"

        try:
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
        
    def get_user(self, user_id):
        """
        extracts all the users from the database
        """
        query = f"SELECT * FROM trueprice.users where id = {user_id};"

        try:
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
        
    
    def delete_user(self, user_id):
        """
        delete the users from the database
        """
        query = f"DELETE FROM trueprice.users WHERE id={user_id};"

        try:
            self.engine.execute(query)
            return True
        except:
            return False
        
    def update_user(self, user_id, prv_level):
        """
        update user inside the application
        """
        query = f"UPDATE trueprice.users SET privileged_level = '{prv_level}' WHERE id={user_id};"

        try:
            self.engine.execute(query)
            return True
        except:
            return False
        
    def update_password(self, old_pswd, new_pswd, email):
        """
        update the password
        """
        old_salted_password = self.secret_salt + old_pswd 
        hashed_old_salted_password = hashlib.sha512(old_salted_password.encode()).hexdigest()

        new_salted_password = self.secret_salt + new_pswd 
        hashed_new_salted_password = hashlib.sha512(new_salted_password.encode()).hexdigest()
        

        query = f"UPDATE trueprice.users SET password = '{hashed_new_salted_password}' WHERE email='{email}' and password ='{hashed_old_salted_password}';"

        try:
            self.engine.execute(query)
            return True
        except:
            return False





