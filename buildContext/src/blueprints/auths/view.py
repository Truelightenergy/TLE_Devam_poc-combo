import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .util import Util
from .auth_model import AuthUtil
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.keys import secret_key, secret_salt
from utils.blocked_tokens import revoked_jwt


auths = Blueprint('auths', __name__,
                    template_folder="../templates/",
                    static_folder='static')



db_obj = AuthUtil(secret_key, secret_salt)
api_util = Util(secret_key, secret_salt)
roles = RolesDecorator(revoked_jwt)


def setup_session(auth_token):
    """
    setup the session for the api requests
    """

    payload = db_obj.decode_auth_token(auth_token)[1]
    session["jwt_token"] = auth_token
    session["user"] = payload["client_email"]
    session["level"] = payload["role"]


@auths.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Signup to the application.
    ---
    tags:
      - Authentication
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: Email address
      - name: password
        in: query
        type: string
        required: true
        description: Password
    responses:
      200:
        description: Signup successful
      400:
        description: Incorrect parameters
      403:
        description: Signup failed
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    

    if rest_api_condition:
        if not (request.args.get("email") and request.args.get("password")):
            return jsonify({"error": "Incorrect Params"}), 400
        email = request.args.get("email")
        password = request.args.get("password")
        json_obj, status_code = api_util.signup(email, password)
        return jsonify(json_obj), status_code
    
    else:
        if request.method=="POST":
            email = request.form.get("email")
            password = request.form.get("password")
            json_obj, status_code = api_util.signup(email, password)
            if json_obj["message_flag"]== "success":
                return render_template('auths/signup.html',  flash_message=True, message_toast = "Signup Successfully", message_flag = "success"), 200
            else:
                return render_template('auths/signup.html',  flash_message=True, message_toast = "Signup Failed", message_flag = "error"), 403
        else:
            return render_template('auths/signup.html')
        

@auths.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login to the application.
    ---
    tags:
      - Authentication
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: Email address
      - name: password
        in: query
        type: string
        required: true
        description: Password
    responses:
      200:
        description: Login successful
      400:
        description: Incorrect parameters
      403:
        description: Login failed
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    

    if rest_api_condition:
        email = request.args.get('email')
        pswd = request.args.get('password')
        json_obj, status_code = api_util.login(email, pswd)
        return jsonify(json_obj), status_code
    else:
        if request.method=="POST":
            email = request.form.get('email')
            pswd = request.form.get('password')
            json_obj, status_code = api_util.login(email, pswd)
            if json_obj["message_flag"] == "success":
                return api_util.application_startup()
            else:
                return render_template('auths/login.html',  flash_message=True, message_toast = "Login Failed", message_flag = "error"), 403
        else:
            return render_template('auths/login.html')

    
@auths.route('/logout', methods=['GET', 'POST'])
@roles.readonly_token_required
def logout():
    """
    Logout from the application.
    ---
    tags:
      - Authentication
    security:
        - Bearer: []
    responses:
      200:
        description: Logout successful
      302:
        description: Redirect to login page
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        revoked_jwt.add(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.logout()
        return jsonify(json_obj), status_code
    else:
        json_obj, status_code = api_util.logout()
        return redirect(url_for("auths.login"))
    

@auths.route('/', methods=['GET', 'POST'])
@roles.readonly_token_required
def index():
    """
    start up aplications
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        response = api_util.application_startup()
        jsonify({"msg": "Index Page"}), 200
    else:
        response = api_util.application_startup()
        return response
    
@auths.route('/home', methods=['GET', 'POST'])
@roles.readonly_token_required
def home():
    """
    start up aplications
    """
    return render_template("auths/index.html")

@auths.route('/create_user', methods=['GET', 'POST'])
@roles.admin_token_required
def create_user():
    """
    create users for the applications #ADMIN
    ---
    tags:
      - Users
    security:
        - Bearer: []
    parameters:
      - name: prv_level
        in: query
        type: string
        required: true
        description: User's privilege level
      - name: email
        in: query
        type: string
        required: true
        description: User's email address
      - name: password
        in: query
        type: string
        required: true
        description: User's password
    responses:
      200:
        description: User creation successful
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to create user
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("email") and request.args.get("password")  and request.args.get("prv_level")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        prv_level, email, pswd= request.args.get('prv_level'), request.args.get("email"),request.args.get("password")
        json_obj, status_code = api_util.create_user(email, pswd, prv_level)
        return jsonify(json_obj), status_code
    else:
        if request.method=="POST":

            prv_level, email, pswd= request.form.get('prv_level'), request.form.get("email"),request.form.get("password")
            json_obj, status_code = api_util.create_user(email, pswd, prv_level)
            if json_obj["message_flag"]== "success":
                return render_template('auths/create_user.html', flash_message=True, message_toast = "User Created", message_flag = "success")
            else:
                return render_template('auths/create_user.html', flash_message=True, message_toast = "Unable to create user", message_flag = "error")
        else:
            return render_template("auths/create_user.html")
        

@auths.route('/view_user', methods=['GET', 'POST'])
@roles.admin_token_required
def view_user():
    """
    view all user of applications #ADMIN
    ---
    tags:
      - Users - View User API
    security:
        - Bearer: []
    responses:
      200:
        description: View All user
      302:
        description: Redirect to login page
    
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        return jsonify(db_obj.get_all_users_data()),200
        
    else:
        json_obj, status_code  = api_util.view_user()
        return render_template("auths/view_user.html", data = json_obj["data"])
    

# application endpoint
@auths.route('/disable_user_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_user_ui():
    """
    Disable user from ui side
    ---
    tags:
      - Users - Disable  User UI
    security:
        - Bearer: []
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
        description: User ID to disable 
    responses:
      200:
        description: User disabled successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to disable user
    """

    user_id = request.args.get('user_id')
    if not user_id:
        record = db_obj.get_all_users()
        return render_template('auths/view_user.html', data=record)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("user_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.enable_disable_user(user_id, "disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.enable_disable_user(user_id, "disabled")
        record = db_obj.get_all_users()
        if json_obj["message_flag"]== "success":
            return render_template('auths/view_user.html', flash_message=True, message_toast = "User Disabled", message_flag = "success", data = record)                
        else:
            return render_template('auths/view_user.html', flash_message=True, message_toast = "Unable to disable user", message_flag = "error", data = record)
                    
        
            
# api endpoint
@auths.route('/disable_user', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_user_using_email():
    """
    Disable user from api
    ---
    tags:
      - Users - Disable  User API
    security:
        - Bearer: []
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: User Email to disable 
    responses:
      200:
        description: User disabled successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to disable user
    """
    if not (request.args.get("email")):
            return jsonify({"error": "Incorrect Params"}), 400
    email = request.args.get("email")
    setup_session(request.headers['Authorization'].split()[-1])
    json_obj, status_code = api_util.enable_disable_user_from_api(email, "disabled")
    return jsonify(json_obj), status_code



# application endpoint
@auths.route('/enable_user_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_user_ui():
    """
    Enable user from ui side
    ---
    tags:
      - Users - Enable User UI
    security:
        - Bearer: []
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
        description: User ID to enable 
    responses:
      200:
        description: User enable successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to enable user
    """
    user_id = request.args.get('user_id')
    if not user_id:
        record = db_obj.get_all_users()
        return render_template('auths/view_user.html', data=record)
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("user_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.enable_disable_user(user_id, "enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.enable_disable_user(user_id, "enabled")
        record = db_obj.get_all_users()
        if json_obj["message_flag"]== "success":
            return render_template('auths/view_user.html', flash_message=True, message_toast = "User Disabled", message_flag = "success", data = record)                
        else:
            return render_template('auths/view_user.html', flash_message=True, message_toast = "Unable to disable user", message_flag = "error", data = record)
           
# api endpoint
@auths.route('/enable_user', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_user_using_email():
    """
    Enable user from api
    ---
    tags:
      - Users - Enable User API
    security:
        - Bearer: []
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: User Email to enable 
    responses:
      200:
        description: User enable successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to enable user
    """
    email = request.args.get("email")
    if not (request.args.get("email")):
            return jsonify({"error": "Incorrect Params"}), 400
    setup_session(request.headers['Authorization'].split()[-1])
    json_obj, status_code = api_util.enable_disable_user_from_api(email, "enabled")
    return jsonify(json_obj), status_code

# application endpoint
@auths.route('/update_user_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def update_user_ui():
    """
    enable particular user
    ---
    tags:
        - Users - Update User UI
    security:
        - Bearer: []
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
        description: User ID to update
      - name: prv_level
        in: query
        type: string
        required: true
        description: User's new privilege level
    responses:
      200:
        description: User updated successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to update user
    """
    user_id = request.args.get('user_id')
    if not user_id:
        record = db_obj.get_all_users()
        return render_template('auths/view_user.html', data=record)
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        if not (request.args.get("user_id") and request.args.get('prv_level')):
            return jsonify({"error": "Incorrect Params"}), 400
        
        prv_level= request.args.get('prv_level') 
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.update_user(user_id, prv_level)
        return jsonify(json_obj), status_code
    else:
        if request.method == 'POST':
            prv_level= request.form.get('prv_level') 
            json_obj, status_code = api_util.update_user(user_id, prv_level)
            record = db_obj.get_all_users()
            if json_obj["message_flag"]== "success":
                return render_template('auths/view_user.html', flash_message=True, message_toast = "User Updated", message_flag = "success", data = record)                
            else:
                return render_template('auths/view_user.html', flash_message=True, message_toast = "Unable to update user", message_flag = "error", data = record)
        else:
            record = db_obj.get_user(user_id)
            return render_template("auths/update_user.html", data = record)
   
# api endpoint
@auths.route('/update_user', methods=['GET', 'POST'])
@roles.admin_token_required
def update_user_from_api():
    """
    enable particular user using api
    ---
    tags:
        - Users - Update User API
    security:
        - Bearer: []
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: User Email to update
      - name: prv_level
        in: query
        type: string
        required: true
        description: User's new privilege level
    responses:
      200:
        description: User updated successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to update user
    """

    setup_session(request.headers['Authorization'].split()[-1])
    json_obj, status_code = api_util.update_user_from_api()
    return jsonify(json_obj), status_code




# application endpoint
@auths.route('/reset_password_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def reset_password_ui():
    """
    reset password of particular user 
     
    ---
    tags:
      - Users - Password Reset UI
    security:
        - Bearer: []
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
        description: User Id to reset its password
    responses:
      200:
        description: User' password reset successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to reset password of user
    """

    user_id = request.args.get('user_id')
    if not user_id:
        record = db_obj.get_all_users()
        return render_template('auths/view_user.html', data=record)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("user_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.reset_password(user_id)
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.reset_password(user_id)
        record = db_obj.get_all_users()
        if json_obj["message_flag"] == "success":
            return render_template('auths/view_user.html', flash_message=True, message_toast = "Reset Password", message_flag = "success", data = record)                
        else:
            return render_template('auths/view_user.html', flash_message=True, message_toast = "Unable to to reset Password", message_flag = "error", data = record)
                    
        
            
# api endpoint
@auths.route('/reset_password', methods=['GET', 'POST'])
@roles.admin_token_required
def reset_password():
    """
    reset password of particular user 
     
    ---
    tags:
      - Users - Password Reset API
    security:
        - Bearer: []
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: Email to reset its password
    responses:
      200:
        description: User' password reset successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to reset password of user
    """
    if not (request.args.get("email")):
            return jsonify({"error": "Incorrect Params"}), 400
    email = request.args.get("email")
    setup_session(request.headers['Authorization'].split()[-1])
    json_obj, status_code = api_util.reset_password_from_api(email)
    return jsonify(json_obj), status_code



@auths.route('/update_password', methods=['GET', 'POST'])
@roles.readonly_token_required
def update_password():
    """
    Update your password
    ---
    tags:
        - Users - Update Password
    security:
        - Bearer: []
    parameters:
      - name: old_password
        in: query
        type: string
        required: true
        description: Old password

      - name: password
        in: query
        type: string
        required: true
        description: New Password
      
    responses:
      200:
        description: password updated successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to update password
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        if not (request.args.get("old_password") and request.args.get("password")):
            return jsonify({"error": "Incorrect Params"}), 400
        
        setup_session(request.headers['Authorization'].split()[-1])
        email, old_pswd, new_pswd = session["user"], request.args.get("old_password"), request.args.get("password")
        json_obj, status_code = api_util.update_password(email, old_pswd, new_pswd )
        
        return jsonify(json_obj), status_code
    else:
        if request.method == 'POST':
            email, old_pswd, new_pswd = session["user"], request.form.get("old_password"), request.form.get("password")
            json_obj, status_code = api_util.update_password(email, old_pswd, new_pswd )
            if json_obj["message_flag"] == "success":
                return render_template("auths/update_password.html",  flash_message=True, message_toast = "password updated", message_flag = "success")
            else:
                return render_template("auths/update_password.html",  flash_message=True, message_toast = "unable to update password", message_flag = "error") 
        return render_template("auths/update_password.html")
    




