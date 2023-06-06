import os
from utils.endpoints import Util
from flask import Flask, request, session, jsonify, redirect, url_for, render_template, make_response
from utils.roles import RolesDecorator
from functools import wraps
from utils.auths import Auths
from utils.revoke_tokens import RevokedTokens
from flasgger import Swagger




secret_key = "super-scret-key" #env variable
secret_salt = "secret-salt" #env variable
auth_obj = Auths(secret_key, secret_salt)
api_util = Util(auth_obj)
revoked_jwt = RevokedTokens()
roles = RolesDecorator(auth_obj, revoked_jwt)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = api_util.UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key' #env variable

template = {
    "securityDefinitions": {
        "Bearer":
            {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                 'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
            }
    }
}



swagger = Swagger(app, template=template)


def setup_session(auth_token):
    """
    setup the session for the api requests
    """

    payload = auth_obj.decode_auth_token(auth_token)[1]
    session["jwt_token"] = auth_token
    session["user"] = payload["client_email"]
    session["level"] = payload["role"]




@app.route('/signup', methods=['GET', 'POST'])
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
            if status_code==200:
                return render_template('signup.html',  flash_message=True, message_toast = "Signup Successfully", message_flag = "success"), 200
            else:
                return render_template('signup.html',  flash_message=True, message_toast = "Signup Failed", message_flag = "error"), 403
        else:
            return render_template('signup.html')
        

@app.route('/login', methods=['GET', 'POST'])
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
            if status_code==200:
                return api_util.application_startup()
            else:
                return render_template('login.html',  flash_message=True, message_toast = "Login Failed", message_flag = "error"), 403
        else:
            return render_template('login.html')

    
@app.route('/logout', methods=['GET', 'POST'])
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
        return redirect(url_for("login"))

@app.route('/create_user', methods=['GET', 'POST'])
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
            if status_code==200:
                return render_template('create_user.html', flash_message=True, message_toast = "User Created", message_flag = "success")
            else:
                return render_template('create_user.html', flash_message=True, message_toast = "Unable to create user", message_flag = "error")
        else:
            return render_template("create_user.html")


@app.route('/view_user', methods=['GET', 'POST'])
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
        description: All user
      302:
        description: Redirect to login page
    
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        return jsonify(auth_obj.get_all_users_data()),200
        
    else:
        json_obj, status_code  = api_util.view_user()
        return render_template("view_user.html", data = json_obj["data"])
    



# application endpoint
@app.route('/disable_user_ui', methods=['GET', 'POST'])
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
        record = auth_obj.get_all_users()
        return render_template('view_user.html', data=record)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("user_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.enable_disable_user(user_id, "disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.enable_disable_user(user_id, "disabled")
        record = auth_obj.get_all_users()
        if status_code==200:
            return render_template('view_user.html', flash_message=True, message_toast = "User Disabled", message_flag = "success", data = record)                
        else:
            return render_template('view_user.html', flash_message=True, message_toast = "Unable to disable user", message_flag = "error", data = record)
                    
        
            
# api endpoint
@app.route('/disable_user', methods=['GET', 'POST'])
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
@app.route('/enable_user_ui', methods=['GET', 'POST'])
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
        record = auth_obj.get_all_users()
        return render_template('view_user.html', data=record)
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("user_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.enable_disable_user(user_id, "enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.enable_disable_user(user_id, "enabled")
        record = auth_obj.get_all_users()
        if status_code==200:
            return render_template('view_user.html', flash_message=True, message_toast = "User Disabled", message_flag = "success", data = record)                
        else:
            return render_template('view_user.html', flash_message=True, message_toast = "Unable to disable user", message_flag = "error", data = record)
           
# api endpoint
@app.route('/enable_user', methods=['GET', 'POST'])
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
@app.route('/update_user_ui', methods=['GET', 'POST'])
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
        record = auth_obj.get_all_users()
        return render_template('view_user.html', data=record)
    
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
            record = auth_obj.get_all_users()
            if status_code==200:
                return render_template('view_user.html', flash_message=True, message_toast = "User Updated", message_flag = "success", data = record)                
            else:
                return render_template('view_user.html', flash_message=True, message_toast = "Unable to update user", message_flag = "error", data = record)
        else:
            record = auth_obj.get_user(user_id)
            return render_template("update_user.html", data = record)
   
# api endpoint
@app.route('/update_user', methods=['GET', 'POST'])
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
@app.route('/reset_password_ui', methods=['GET', 'POST'])
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
        record = auth_obj.get_all_users()
        return render_template('view_user.html', data=record)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("user_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.reset_password(user_id)
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.reset_password(user_id)
        record = auth_obj.get_all_users()
        if status_code==200:
            return render_template('view_user.html', flash_message=True, message_toast = "Reset Password", message_flag = "success", data = record)                
        else:
            return render_template('view_user.html', flash_message=True, message_toast = "Unable to to reset Password", message_flag = "error", data = record)
                    
        
            
# api endpoint
@app.route('/reset_password', methods=['GET', 'POST'])
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
        description: User Id to reset its password
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



@app.route('/update_password', methods=['GET', 'POST'])
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
        print(email, old_pswd, new_pswd)
        json_obj, status_code = api_util.update_password(email, old_pswd, new_pswd )
        
        return jsonify(json_obj), status_code
    else:
        if request.method == 'POST':
            email, old_pswd, new_pswd = session["user"], request.form.get("old_password"), request.form.get("password")
            json_obj, status_code = api_util.update_password(email, old_pswd, new_pswd )
            if status_code==200:
                return render_template("update_password.html",  flash_message=True, message_toast = "password updated", message_flag = "success")
            else:
                return render_template("update_password.html",  flash_message=True, message_toast = "unable to update password", message_flag = "error") 
        return render_template("update_password.html")


@app.route('/', methods=['GET', 'POST'])
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
    
@app.route('/home', methods=['GET', 'POST'])
@roles.readonly_token_required
def home():
    """
    start up aplications
    """
    return render_template("index.html")

# figure out how to get with curl as well
@app.route('/upload_csv', methods=['GET','POST'])
@roles.readwrite_token_required
def upload_csv():
    """
    handles the csv file uploads
    ---
    tags:
      - Uploads CSV
    security:
        - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The CSV file to upload
    responses:
      200:
        description: Data inserted successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to insert data
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition and ("acceptance" not in session):
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.upload_csv()
        return jsonify(json_obj), status_code
        pass
    else:
        
        if request.method=="POST":
            json_obj, status_code = api_util.upload_csv()
            session["acceptance"]=None
            
            if status_code==200:
                return render_template('upload_csv.html', flash_message=True, message_toast = "Data Inserted", message_flag = "success")        
            else:    
                return render_template('upload_csv.html', flash_message=True, message_toast = json_obj["message_toast"], message_flag = "error")
        else:
            session["acceptance"] = request.headers.get('Accept')
            return render_template('upload_csv.html')

@app.route('/upload_zip', methods=['GET','POST'])
@roles.readwrite_token_required
def upload_zip():
    """
    handles the zip uploads
    """
    return jsonify({"msg":"Closed Endpoint"})

@app.route('/get_data', methods=['GET','POST'])
@roles.readonly_token_required
def get_data():
    """
    get data from application
    ---
    tags:
        - Users - Downloads
    security:
        - Bearer: []
    parameters:
      - name: start
        in: query
        type: string
        format: date
        required: true
        description: Start Date
    
      - name: end
        in: query
        type: string
        format: date
        required: true
        description: End Date

      - name: curve_type
        in: query
        type: string
        required: true
        description: place the curve type

      - name: iso
        in: query
        type: string
        required: true
        description: place the ISO

      - name: strip
        in: query
        type: string
        required: true
        description: place the strip


      - name: history
        in: query
        type:  boolean
        required: true
        description: true or false

      - name: type
        in: query
        type: string
        required: true
        description: CSV or JSON
      
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
        setup_session(request.headers['Authorization'].split()[-1])
    args = request.args.to_dict()
    args['strip'] = request.args.getlist('strip')
    if request.args.get('history')=="true":
        args['history'] = True
    else:
        args['history'] = False
    response, status = api_util.extract_data(args)
    if status != "success":
        return status
    return response



@app.route('/download_data', methods=['GET','POST'])
@roles.readonly_token_required
def download_data():
    """
    handles data downloads
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        response, status = api_util.download_data()
    else:
        if request.method == 'POST':
            response, status = api_util.download_data()
            if status != "success":
                return render_template('download_data.html',  flash_message=True, message_toast = status, message_flag = "error")
            else:
                return response
        else:
            return render_template('download_data.html')
        

@app.route('/get_options', methods=['POST'])
@roles.readonly_token_required
def get_options():

    """
    makes the current drop down dynamic
    """
    curve = request.json['curve']
    if curve=="energy":
        option = ["ERCOT", "ISONE", "NYISO","MISO", "PJM"]
    elif curve == "nonenergy":
        option = ["ERCOT", "ISONE", "NYISO","MISO", "PJM"]
    elif curve == "rec":
        option = ["ERCOT", "ISONE", "NYISO", "PJM"]

    return jsonify(option)

@app.route("/log_stream", methods=['GET','POST'])
@roles.admin_token_required
def log_stream():
    """returns logging information"""
    return api_util.stream_logger()

@app.route("/get_logs", methods=['GET','POST'])
@roles.admin_token_required
def get_logs():
    """
    Logs of the application.
    ---
    tags:
      - Logs
    security:
        - Bearer: []
    responses:
      200:
        description: Getting Logs successful
      302:
        description: Unable to get Logs
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        json_obj = api_util.app_logging_api()
        return json_obj,200
    else:
        return render_template("log_streaming.html")  

@app.route('/upload_status', methods=['GET', 'POST'])
@roles.readonly_token_required
def upload_status():
    """
    get recent uploads
    ---
    tags:
      - Recent Uploads
    security:
        - Bearer: []
    responses:
      200:
        description: Uploads status
      302:
        description: Failed
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        return jsonify(auth_obj.get_all_uploads_data()),200
    else:
        json_obj, status_code  = api_util.view_uploads()
        return render_template("upload_status.html", data = json_obj["data"])   
    

@app.route('/maintainance', methods=['GET', 'POST'])
def maintainance():
    """
    view all uploads of applications 
    """
    return render_template("maintainance.html")


# application endpoint
@app.route('/enable_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_ui():
    """
    Enable UI
    ---
    tags:
      - Enable UI
    security:
        - Bearer: []
    responses:
      200:
        description: UI Disabled successful
      302:
        description: Unable to disable UI
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_ui("enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_ui("enabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "UI enabled", message_flag = "success", data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to enable UI", message_flag = "error", data=record)


@app.route('/disable_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_ui():
    """
    Disable UI
    ---
    tags:
      - Disable UI
    security:
        - Bearer: []
    responses:
      200:
        description: UI Disabled successful
      302:
        description: Unable to disable UI
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_ui("disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_ui("disabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "UI disabled", message_flag = "success",data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to disable UI", message_flag = "error", data=record)

# application endpoint
@app.route('/enable_api', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_api():
    """
    ENable API
    ---
    tags:
      - Enable API
    security:
        - Bearer: []
    responses:
      200:
        description: API Enable successful
      302:
        description: Unable to Enable API
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_api("enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_api("enabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "API Enabled", message_flag = "success", data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to enable API", message_flag = "error", data=record)


@app.route('/disable_api', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_api():
    """
    Disable API
    ---
    tags:
      - Disable API
    security:
        - Bearer: []
    responses:
      200:
        description: API Disabled successful
      302:
        description: Unable to disable API
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_api("disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_api("disabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "API disable", message_flag = "success",data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to disable API", message_flag = "error", data=record)


@app.route('/site_control', methods=['GET', 'POST'])
@roles.admin_token_required
def site_control():
    """
    Site Control of the application.
    ---
    tags:
      - Site Control
    security:
        - Bearer: []
    responses:
      200:
        description: Getting Logs successful
      302:
        description: Unable to get Logs
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        return jsonify(auth_obj.get_site_controls_data()),200
        
    else:
        record = auth_obj.get_site_controls()
        return render_template("site_control.html", data = record)
    
    


if __name__ == "__main__":
    print("Starting")
    app.run(port=5555)