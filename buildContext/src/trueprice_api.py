from endpoints_util import Util
from flask import Flask, request, session, jsonify, redirect, url_for, render_template
from functools import wraps
from auths import Auths


secret_key = "super-scret-key"
secret_salt = "secret-salt"
api_util = Util(secret_key, secret_salt)
auth_obj = Auths(secret_key, secret_salt)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = api_util.UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'jwt_token' in session:  
            try:
                flag = auth_obj.decode_auth_token(session["jwt_token"])
                if not flag:
                    return redirect(url_for("login"))
            except:
                return redirect(url_for("login"))      
        else:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return wrap

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    login to the applications
    """
    
    response = api_util.login()
    return response   

    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    logout to the applications
    """
    
    response = api_util.logout()
    return response

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    """
    create users for the applications
    """
    if session["level"]=="admin" :
        response = api_util.create_user()
        return response
    else:
        return redirect(url_for("login"))
    
@app.route('/view_user', methods=['GET', 'POST'])
def view_user():
    """
    view all user of applications
    """
    if session["level"]=="admin":
        response = api_util.view_user()
        return response
    else:
        return redirect(url_for("login"))

@app.route('/delete_user/<user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    """
    delete particular user
    """

    if session["level"]=="admin":
        response = api_util.delete_user(user_id)
        return response
    else:
        return redirect(url_for("login"))
    
@app.route('/update_user/<user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    """
    delete particular user
    """

    if session["level"]=="admin":
        response = api_util.update_user(user_id)
        return response
    else:
        return redirect(url_for("login"))
    

@app.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    """
    update your password
    """
    response = api_util.update_password()
    return response



@app.route('/', methods=['GET'])
@login_required
def index():
    """
    start up aplications
    """
    response = api_util.application_startup()
    return response


# figure out how to get with curl as well
@app.route('/upload_csv', methods=['GET','POST'])
@login_required
def upload_csv():
    """
    handles the csv file uploads
    """
    if session["level"]=="admin" or session["level"]=="read_write_user":
        response = api_util.upload_csv()
        return response
    else:
        return redirect(url_for("login"))



@app.route('/upload_zip', methods=['GET','POST'])
@login_required
def upload_zip():
    """
    handles the zip uploads
    """
    if session["level"]=="admin" or session["level"]=="read_write_user":
        response = api_util.upload_zip()
        return response
    else:
        return redirect(url_for("login"))


@app.route('/get_data', methods=['GET','POST'])
@login_required
def get_data():
    """
    Extracts the data based on the query strings
    """
    args = request.args.to_dict()
    response, status = api_util.extract_data(args)
    if status != "success":
        return status
    return response


@app.route('/download_data', methods=['GET','POST'])
@login_required
def download_data():
    """
    handles data downloads
    """
    response = api_util.download_data()
    return response

@app.route("/log_stream", methods=['GET','POST'])
def log_stream():
    """returns logging information"""
    return api_util.stream_logger()

@app.route("/get_logs", methods=['GET','POST'])
def get_logs():
    """returns logging information"""
    return render_template("log_streaming.html")       

if __name__ == "__main__":
    print("Starting")
    app.run(port=5555)