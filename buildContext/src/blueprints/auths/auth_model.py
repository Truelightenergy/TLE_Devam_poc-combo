"""
creates the model of the auth operations
"""
import jwt
import hashlib
import datetime
from utils.database_connection import ConnectDatabase

class AuthUtil:

    """
    creates the model of the auth operations
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
        

    def update_user(self, user_id, prv_level):
        """
        update user inside the application
        """
        try:
            query = f"UPDATE trueprice.users SET privileged_level = '{prv_level}' WHERE id={user_id};"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def update_user_using_email(self, user_email, prv_level):
        """
        update user from the api
        """
        try:
            query = f"UPDATE trueprice.users SET privileged_level = '{prv_level}' WHERE email='{user_email}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False



    def create_user(self, client_email, client_password, level):
        """
        creating a new user for now
        """

        try:
            salted_password = self.secret_salt + client_password 
            hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
            query = f"INSERT INTO trueprice.users(email, password, privileged_level) VALUES ('{client_email}', '{hashed_salted_password}', '{level}');"
        
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except :
            return False
        
    def authenticate_user(self, client_email, client_password):
        """
        authenticate user based on given credentials
        """
        try:
            salted_password = self.secret_salt + client_password 
            hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
            query = f"SELECT * FROM trueprice.users WHERE email = '{client_email}' AND password = '{hashed_salted_password}' AND status = 'enabled';"

            results = self.engine.execute(query).fetchall()
            flag = False
            admin_check = False
            for row in results:
                flag = True
                admin_check = row['privileged_level']
            return flag, admin_check
        except:
            return False, False
        
    def encode_auth_token(self, client_email, client_password, client_role):
        """
        Generates the Auth Token
        
        """

        try:
            salted_password = self.secret_salt + client_password 
            hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()
        
            payload = {'client_email': client_email, 
                        'client_password' : hashed_salted_password,
                        'role': client_role,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}
            token = jwt.encode(payload,
                        self.secret_key, "HS256")
            return True, token
        except:
            return False, None
        
    
    def enable_disable_user(self, user_id, status):
        """
        disables or enables user based on thier id
        """
        try:
            query = f"UPDATE trueprice.users SET status = '{status}' WHERE id={user_id};"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def enable_disable_user_using_email(self, user_email, status):
        """
        disables or enables user based on their emails
        """

        try:
            query = f"UPDATE trueprice.users SET status = '{status}'  WHERE email='{user_email}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def get_user_email(self, user_id):
        """
        get email of user based on the id
        """

        try:
            query = f"select * from trueprice.users where id={user_id};"
            results = self.engine.execute(query).fetchall()
            mail = None
            for row in results:
                mail = row['email']
                break
            return mail
        
        except:
            return None
        
    def reset_user_password(self, user_id, password):
        """
        reset users password
        """

        salted_password = self.secret_salt + password 
        hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()

        try:
            query = f"UPDATE trueprice.users SET password = '{hashed_salted_password}' WHERE id = {user_id};"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        

    def reset_user_password_for_api(self, email):
        """
        reset users password
        """

        salted_password = self.secret_salt + email 
        hashed_salted_password = hashlib.sha512(salted_password.encode()).hexdigest()

        try:
            query = f"UPDATE trueprice.users SET password = '{hashed_salted_password}' WHERE email = '{email}';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def update_password(self, old_pswd, new_pswd, email):
        """
        update the password
        """
        try:
            old_salted_password = self.secret_salt + old_pswd 
            hashed_old_salted_password = hashlib.sha512(old_salted_password.encode()).hexdigest()

            new_salted_password = self.secret_salt + new_pswd 
            hashed_new_salted_password = hashlib.sha512(new_salted_password.encode()).hexdigest()
            

            query = f"UPDATE trueprice.users SET password = '{hashed_new_salted_password}' WHERE email='{email}' and password ='{hashed_old_salted_password}';"

            
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        

    def switch_api(self, status):
        """
        switch enable or disable
        """
        if status not in ["enabled", "disabled"]:
            status = "enabled"

        try:
            query = f"UPDATE trueprice.site SET api_status = '{status}'  WHERE admin='tle_admin';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def switch_ui(self, status):
        """
        switch enable or disable
        """
        if status not in ["enabled", "disabled"]:
            status = "enabled"

        try:
            query = f"UPDATE trueprice.site SET ui_status = '{status}'  WHERE admin='tle_admin';"
            result = self.engine.execute(query)
            if result.rowcount > 0:
                return True
            return False
        except:
            return False
        
    def verify_api(self):
        """
        verify api is enabled
        """
        try:
            query = f" SELECT * from trueprice.site  WHERE admin='tle_admin' AND api_status ='enabled';"
            results = self.engine.execute(query).fetchall()
            flag = False
            for row in results:
                flag = True
            return flag
        except:
            return False
        
    def verify_ui(self):
        """
        verify ui is enabled
        """
        try:
            query = f" SELECT * from trueprice.site  WHERE admin='tle_admin' AND ui_status ='enabled';"
            results = self.engine.execute(query).fetchall()
            flag = False
            for row in results:
                flag = True
            return flag
        except:
            return False
        
    def get_all_users_data(self):
        """
        extracts all the users from the database
        """
        try:
            query = f"SELECT * FROM trueprice.users;"
            emails = []
            levels = []
        
            response = self.engine.execute(query).fetchall()
            for row in response:
                emails.append(row["email"])
                levels.append(row["privileged_level"])
            results = {
                "email": emails,
                "privileged_level": levels
            }


            return results
        except:
            return None
        
    def get_user(self, user_id):
        """
        extracts all the users from the database
        """
        try:
            query = f"SELECT * FROM trueprice.users where id = {user_id};"
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None