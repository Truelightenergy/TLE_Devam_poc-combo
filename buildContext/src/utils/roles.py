from functools import wraps
from flask import session, request, jsonify, url_for, redirect, make_response
from utils.auths import Auths


class RolesDecorator:
    def __init__(self, auth_obj, revoked_jwt):
        self.auth_obj = auth_obj
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
            token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else session.get('jwt_token')
            if not token:
                return jsonify({'message': 'Token is missing'}) if 'Authorization' in request.headers else self.login()
            if token in self.revoked_jwt:
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()
            try:
                data = self.auth_obj.decode_auth_token(token)[1]
                user_role = data['role']
                email = data["client_email"]
            except:
                return jsonify({'message': 'Token is Invalid'}) if 'Authorization' in request.headers else self.login()

            if user_role not in ('read_only_user', 'admin', 'read_write_user'):
                return jsonify({'message': 'Unauthorized access'}) if 'Authorization' in request.headers else self.login()
            if not self.auth_obj.verify_user_status(email):
                return jsonify({'message': 'User Disabled'}) if 'Authorization' in request.headers else self.login()

            if user_role !="admin":
                if 'Authorization' in request.headers:
                    if not self.auth_obj.verify_api():
                        return jsonify({'message': 'API Disabled'})
                else:
                    if not self.auth_obj.verify_ui():
                        return self.maintainance()



            return f(*args, **kwargs)
        return decorated_function
    

    def readwrite_token_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else session.get('jwt_token')
            if not token:
                return jsonify({'message': 'Token is missing'}) if 'Authorization' in request.headers else self.login()
            if token in self.revoked_jwt:
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()
            try:
                data = self.auth_obj.decode_auth_token(token)[1]
                user_role = data['role']
                email = data["client_email"]
            except:
                return jsonify({'message': 'Token is Invalid'}) if 'Authorization' in request.headers else self.login()

            if user_role not in ('admin', 'read_write_user'):
                return jsonify({'message': 'Unauthorized access'}) if 'Authorization' in request.headers else self.login()
            
            if not self.auth_obj.verify_user_status(email):
                return jsonify({'message': 'User Disabled'}) if 'Authorization' in request.headers else self.login()
            
            if user_role !="admin":
                if 'Authorization' in request.headers:
                    if not self.auth_obj.verify_api():
                        return jsonify({'message': 'API Disabled'})
                else:
                    if not self.auth_obj.verify_ui():
                        return self.maintainance()

            return f(*args, **kwargs)
        return decorated_function


    def admin_token_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else session.get('jwt_token')
            if not token:
                return jsonify({'message': 'Token is missing'}) if 'Authorization' in request.headers else self.login()
            if token in self.revoked_jwt:
                return jsonify({'message': 'Token is expired'}) if 'Authorization' in request.headers else self.login()
            try:
                data = self.auth_obj.decode_auth_token(token)[1]
                user_role = data['role']
                email = data["client_email"]
            except:
                return jsonify({'message': 'Token is Invalid'}) if 'Authorization' in request.headers else self.login()

            if user_role not in ('admin'):
                return jsonify({'message': 'Unauthorized access'}) if 'Authorization' in request.headers else self.login()
            
            if not self.auth_obj.verify_user_status(email):
                return jsonify({'message': 'User Disabled'}) if 'Authorization' in request.headers else self.login()

            return f(*args, **kwargs)
        return decorated_function