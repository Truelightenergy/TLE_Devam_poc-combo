from utils.endpoints import Util
from flask import Flask, request, session, jsonify, redirect, url_for, render_template
from utils.roles import RolesDecorator
from functools import wraps
from utils.auths import Auths
from utils.revoke_tokens import RevokedTokens



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
    signup to the applications
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    

    if rest_api_condition:
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
                return render_template('signup.html',  flash_message=True, message_toast = "Signup Successfully", message_flag = "success", page_type = "download"), 200
            else:
                return render_template('signup.html',  flash_message=True, message_toast = "Login Failed", message_flag = "error", page_type = "download"), 403
        else:
            return render_template('signup.html')
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    login to the applications
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    

    if rest_api_condition:
        json_obj, status_code = api_util.login()
        return jsonify(json_obj), status_code
    else:
        if request.method=="POST":
            json_obj, status_code = api_util.login()
            if status_code==200:
                return api_util.application_startup()
            else:
                return render_template('login.html',  flash_message=True, message_toast = "Login Failed", message_flag = "error", page_type = "download"), 403
        else:
            return render_template('login.html')

    
@app.route('/logout', methods=['GET', 'POST'])

def logout():
    """
    logout to the applications
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        revoked_jwt.add(request.headers['Authorization'].split()[1])
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
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        prv_level, email, pswd= request.args.get('prv_level'), request.args.get("email"),request.args.get("password")
        json_obj, status_code = api_util.create_user(email, pswd, prv_level)
        return jsonify(json_obj), status_code
    else:
        if request.method=="POST":

            prv_level, email, pswd= request.form.get('prv_level'), request.form.get("email"),request.form.get("password")
            json_obj, status_code = api_util.create_user(email, pswd, prv_level)
            if status_code==200:
                return render_template('create_user.html', flash_message=True, message_toast = "User Created", message_flag = "success", page_type = "download")
            else:
                return render_template('create_user.html', flash_message=True, message_toast = "Unable to create user", message_flag = "error", page_type = "download")
        else:
            return render_template("create_user.html")


@app.route('/view_user', methods=['GET', 'POST'])
@roles.admin_token_required
def view_user():
    """
    view all user of applications #ADMIN
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        return jsonify(auth_obj.get_all_users_data()),200
        
    else:
        json_obj, status_code  = api_util.view_user()
        return render_template("view_user.html", data = json_obj["data"])
    



# application endpoint
@app.route('/disable_user/<user_id>', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_user(user_id):
    """
    delete particular user ADIMN
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.enable_disable_user(user_id, "disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.enable_disable_user(user_id, "disabled")
        record = auth_obj.get_all_users()
        if status_code==200:
            return render_template('view_user.html', flash_message=True, message_toast = "User disabled", message_flag = "success", page_type = "download", data=record)
        else:
            return render_template('view_user.html', flash_message=True, message_toast = "Unable to disable user", message_flag = "error", page_type = "download", data=record)
        
# api endpoint
@app.route('/disable_user', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_user_using_email():
    """
    disable particular user ADIMN
    """
    email = request.args.get("email")
    setup_session(request.headers['Authorization'].split()[1])
    json_obj, status_code = api_util.enable_disable_user_from_api(email, "disabled")
    return jsonify(json_obj), status_code



# application endpoint
@app.route('/enable_user/<user_id>', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_user(user_id):
    """
    disable particular user ADIMN
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.enable_disable_user(user_id, "enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.enable_disable_user(user_id, "enabled")
        record = auth_obj.get_all_users()
        if status_code==200:
            return render_template('view_user.html', flash_message=True, message_toast = "User enabled", message_flag = "success", page_type = "download", data=record)
        else:
            return render_template('view_user.html', flash_message=True, message_toast = "Unable to enable user", message_flag = "error", page_type = "download", data=record)
        
# api endpoint
@app.route('/enable_user', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_user_using_email():
    """
    enable particular user ADIMN
    """
    email = request.args.get("email")
    setup_session(request.headers['Authorization'].split()[1])
    json_obj, status_code = api_util.enable_disable_user_from_api(email, "enabled")
    return jsonify(json_obj), status_code

# application endpoint
@app.route('/update_user/<user_id>', methods=['GET', 'POST'])
@roles.admin_token_required
def update_user(user_id):
    """
    enable particular user
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.update_user(user_id)
        return jsonify(json_obj), status_code
    else:
        if request.method == 'POST':
            json_obj, status_code = api_util.update_user(user_id)
            record = auth_obj.get_all_users()
            if status_code==200:
                return render_template('view_user.html', flash_message=True, message_toast = "User Updated", message_flag = "success", page_type = "download", data = record)
            else:
                return render_template('view_user.html', flash_message=True, message_toast = "Unable to update user", message_flag = "error", page_type = "download", data = record)
        else:
            record = auth_obj.get_user(user_id)
            return render_template("update_user.html", data = record)
        
# api endpoint
@app.route('/update_user', methods=['GET', 'POST'])
@roles.admin_token_required
def update_user_from_api():
    """
    delete particular user
    """

    setup_session(request.headers['Authorization'].split()[1])
    json_obj, status_code = api_util.update_user_from_api()
    return jsonify(json_obj), status_code


@app.route('/update_password', methods=['GET', 'POST'])
@roles.readonly_token_required
def update_password():
    """
    update your password
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        email, old_pswd, new_pswd = session["user"], request.args.get("old_password"), request.args.get("password")
        print(email, old_pswd, new_pswd)
        json_obj, status_code = api_util.update_password(email, old_pswd, new_pswd )
        
        return jsonify(json_obj), status_code
    else:
        if request.method == 'POST':
            email, old_pswd, new_pswd = session["user"], request.form.get("old_password"), request.form.get("password")
            json_obj, status_code = api_util.update_password(email, old_pswd, new_pswd )
            if status_code==200:
                return render_template("update_password.html",  flash_message=True, message_toast = "password updated", message_flag = "success", page_type = "download")
            else:
                return render_template("update_password.html",  flash_message=True, message_toast = "unable to update password", message_flag = "error", page_type = "download") 
        return render_template("update_password.html")


@app.route('/', methods=['GET', 'POST'])
@roles.readonly_token_required
def index():
    """
    start up aplications
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
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
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition and ("acceptance" not in session):
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.upload_csv()
        return jsonify(json_obj), status_code
        pass
    else:
        
        if request.method=="POST":
            json_obj, status_code = api_util.upload_csv()
            session["acceptance"]=None
            
            if status_code==200:
                return render_template('upload_csv.html', flash_message=True, message_toast = "Data Inserted", message_flag = "success", page_type = "upload")        
            else:    
                return render_template('upload_csv.html', flash_message=True, message_toast = json_obj["message_toast"], message_flag = "error", page_type = "upload")
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
    Extracts the data based on the query strings
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
    args = request.args.to_dict()
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
        setup_session(request.headers['Authorization'].split()[1])
        response, status = api_util.download_data()
    else:
        if request.method == 'POST':
            response, status = api_util.download_data()
            if status != "success":
                return render_template('download_data.html',  flash_message=True, message_toast = status, message_flag = "error", page_type = "download")
            else:
                return response
        else:
            return render_template('download_data.html')

@app.route("/log_stream", methods=['GET','POST'])
@roles.admin_token_required
def log_stream():
    """returns logging information"""
    return api_util.stream_logger()

@app.route("/get_logs", methods=['GET','POST'])
@roles.admin_token_required
def get_logs():
    """returns logging information"""
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
    view all uploads of applications 
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
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
    disable particular user ADIMN
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.switch_ui("enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_ui("enabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "UI enabled", message_flag = "success", page_type = "download", data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to enable UI", message_flag = "error", page_type = "download", data=record)


@app.route('/disable_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_ui():
    """
    disable particular user ADIMN
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.switch_ui("disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_ui("disabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "UI disabled", message_flag = "success", page_type = "download", data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to disable UI", message_flag = "error", page_type = "download", data=record)

# application endpoint
@app.route('/enable_api', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_api():
    """
    disable particular user ADIMN
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.switch_api("enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_api("enabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "API Enabled", message_flag = "success", page_type = "download", data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to enable API", message_flag = "error", page_type = "download", data=record)


@app.route('/disable_api', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_api():
    """
    disable particular user ADIMN
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        json_obj, status_code = api_util.switch_api("disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_api("disabled")
        record = auth_obj.get_site_controls()
        if status_code==200:
            return render_template('site_control.html', flash_message=True, message_toast = "API disable", message_flag = "success", page_type = "download", data=record)
        else:
            return render_template('site_control.html', flash_message=True, message_toast = "Unable to disable API", message_flag = "error", page_type = "download", data=record)


@app.route('/site_control', methods=['GET', 'POST'])
@roles.admin_token_required
def site_control():
    """
    view all status of applications
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[1])
        return jsonify(auth_obj.get_site_controls_data()),200
        
    else:
        record = auth_obj.get_site_controls()
        return render_template("site_control.html", data = record)
    
    


if __name__ == "__main__":
    print("Starting")
    app.run(port=5555)