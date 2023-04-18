from endpoints_util import Util
from flask import Flask, request, session, jsonify
from functools import wraps
from auths import Auths

api_util = Util()
auth_obj = Auths("super-scret-key")
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = api_util.UPLOAD_FOLDER


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'jwt_token' in session:  
            try:
                flag = auth_obj.decode_auth_token(session["jwt_token"])
                if not flag:
                    return jsonify({'message':'Authentication is needed'}) 
            except:
                return jsonify({'message':'Authentication is needed'})        
        else:
            return jsonify({'message':'Authentication is needed'})

        return f(*args, **kwargs)

    return wrap

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    login to the applications
    """

    # email, pswd = "ali.haider@techliance.com", "admin"
    email, pswd = "ali.haider@gmail.com", "notadmin"
    auth_flag, admin_flag = auth_obj.authenticate_user(email, pswd)
    if auth_flag:
        _, jwt_token = auth_obj.encode_auth_token(email, pswd)
        session["jwt_token"] = jwt_token
        session["user"] = email
        session["isadmin"] = admin_flag
        return jsonify({"message": "user logged in"})
    else:
        return jsonify({'message':'User does not exists'})
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    logout to the applications
    """
    
    session["jwt_token"] = None
    session["user"] = None
    session["isadmin"] = None
    session.clear()
    return jsonify({"message": "user logged out"})


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
def upload_csv():
    """
    handles the csv file uploads
    """
    if session["isadmin"]:
        response = api_util.upload_csv()
        return response
    else:
        return jsonify({"message": "you have no access to this endpoint"})



@app.route('/upload_zip', methods=['GET','POST'])
@login_required
def upload_zip():
    """
    handles the zip uploads
    """
    if session["isadmin"]:
        response = api_util.upload_zip()
        return response
    else:
        return jsonify({"message": "you have no access to this endpoint"})

@app.route('/get_data', methods=['GET','POST'])
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
       

if __name__ == "__main__":
    print("Starting")
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(port=5555)
