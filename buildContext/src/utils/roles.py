from functools import wraps
from flask import session, request, jsonify, url_for, redirect, make_response
from utils.db_utils import DataBaseUtils


class RolesDecorator:
    def __init__(self, db_obj, revoked_jwt):
        self.db_obj = db_obj
        self.revoked_jwt = revoked_jwt

    def login(self):
    
        # Redirect to the new URL
        
        response = make_response('')
        response.headers['Location'] = '/login'
        response.status_code = 302
        return response
    
    
    def maintainance(self):
    
        # Redirect to the new URL
        response = make_response('')
        response.headers['Location'] = '/maintainance'
        response.status_code = 302
        return response

    def readonly_token_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
            token = None
            if rest_api_condition:
                if 'Authorization' in request.headers:
                    token = request.headers.get('Authorization', '').split()[-1]
                if token is None and (request.content_type=='application/json'):
                    token = session.get('jwt_token')
            else:
                token = session.get('jwt_token')
                
                


            # if token does not exist
            if not token:
                return jsonify({'message': 'Token is missing'}) if 'Authorization' in request.headers else self.login()
            
            # if token is expired
            if token in self.revoked_jwt:
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()
            
            # if token is valid
            try:
                data = self.db_obj.decode_auth_token(token)[1]
                user_role = data['role']
                email = data["client_email"]
            except:
                return jsonify({'message': 'Token is Invalid'}) if 'Authorization' in request.headers else self.login()
            
            # handling case where no role is available
            if user_role not in ('read_only_user', 'admin', 'read_write_user'):
                return jsonify({'message': 'Unauthorized access'}) if 'Authorization' in request.headers else self.login()
            
            # handling case where user is disabled or not
            if not self.db_obj.verify_user_status(email):
                return jsonify({'message': 'User Disabled'}) if 'Authorization' in request.headers else self.login()
            
            # checking user role is changed or not
            if user_role != self.db_obj.get_user_current_role(email):
                self.revoked_jwt.add(token)
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()

            # api/ui disable check
            if user_role !="admin":
                if 'Authorization' in request.headers:
                    if not self.db_obj.verify_api():
                        return jsonify({'message': 'API Disabled'})
                else:
                    if not self.db_obj.verify_ui():
                        return self.maintainance()



            return f(*args, **kwargs)
        return decorated_function
    

    def readwrite_token_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            
            rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
            token = None
            if rest_api_condition:
                if 'Authorization' in request.headers:
                    token = request.headers.get('Authorization', '').split()[-1]
                if token is None and (request.content_type=='application/json'):
                    token = session.get('jwt_token')
            else:
                token = session.get('jwt_token')

            # if token does not exist
            if not token:
                return jsonify({'message': 'Token is missing'}) if 'Authorization' in request.headers else self.login()
           
            # if token is expired
            if token in self.revoked_jwt:
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()
            
            # if token is valid
            try:
                data = self.db_obj.decode_auth_token(token)[1]
                user_role = data['role']
                email = data["client_email"]
            except:
                return jsonify({'message': 'Token is Invalid'}) if 'Authorization' in request.headers else self.login()

             # handling case where no role is available
            if user_role not in ('admin', 'read_write_user'):
                return jsonify({'message': 'Unauthorized access'}) if 'Authorization' in request.headers else self.login()
            
            # handling case where user is disabled or not
            if not self.db_obj.verify_user_status(email):
                return jsonify({'message': 'User Disabled'}) if 'Authorization' in request.headers else self.login()
            
            # checking user role is changed or not
            if user_role != self.db_obj.get_user_current_role(email):
                self.revoked_jwt.add(token)
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()
            
            # api/ui disable check
            if user_role !="admin":
                if 'Authorization' in request.headers:
                    if not self.db_obj.verify_api():
                        return jsonify({'message': 'API Disabled'})
                else:
                    if not self.db_obj.verify_ui():
                        return self.maintainance()

            return f(*args, **kwargs)
        return decorated_function


    def admin_token_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
            token = None
            if rest_api_condition:
                if 'Authorization' in request.headers:
                    token = request.headers.get('Authorization', '').split()[-1]
                if token is None and (request.content_type == 'application/json'):
                    token = session.get('jwt_token')
            else:
                token = session.get('jwt_token')

             # if token does not exist
            if not token:
                return jsonify({'message': 'Token is missing'}) if 'Authorization' in request.headers else self.login()
            # if token is expired
            if token in self.revoked_jwt:
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()
            
            # if token is valid
            try:
                data = self.db_obj.decode_auth_token(token)[1]
                user_role = data['role']
                email = data["client_email"]
            except:
                return jsonify({'message': 'Token is Invalid'}) if 'Authorization' in request.headers else self.login()

            # handling case where no role is available
            if user_role not in ('admin'):
                return jsonify({'message': 'Unauthorized access'}) if 'Authorization' in request.headers else self.login()
            
            # handling case where user is disabled or not
            if not self.db_obj.verify_user_status(email):
                return jsonify({'message': 'User Disabled'}) if 'Authorization' in request.headers else self.login()
            
             # checking user role is changed or not
            if user_role != self.db_obj.get_user_current_role(email):
                self.revoked_jwt.add(token)
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()

            return f(*args, **kwargs)
        return decorated_function