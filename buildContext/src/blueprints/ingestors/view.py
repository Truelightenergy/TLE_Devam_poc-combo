import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .util import Util
from .ingestor_model import IngestorUtil
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.configs import read_config
from utils.blocked_tokens import revoked_jwt


config = read_config()
ingestors = Blueprint(config['ingestors_path'], __name__,
                    template_folder=config['template_path'],
                    static_folder=config['static_path'])


secret_key = config['secret_key']
secret_salt = config['secret_salt']
db_obj = IngestorUtil(secret_key, secret_salt)
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


@ingestors.route('/upload_csv', methods=['GET','POST'])
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
        
    else:
        
        if request.method=="POST":
            json_obj, status_code = api_util.upload_csv()
            session["acceptance"]=None
            
            if json_obj["message_flag"]== "success":
                return render_template('ingestors/upload_csv.html', flash_message=True, message_toast = "Data Inserted", message_flag = "success")        
            else:    
                return render_template('ingestors/upload_csv.html', flash_message=True, message_toast = json_obj["message_toast"], message_flag = "error")
        else:
            session["acceptance"] = request.headers.get('Accept')
            return render_template('ingestors/upload_csv.html')

@ingestors.route('/upload_zip', methods=['GET','POST'])
@roles.readwrite_token_required
def upload_zip():
    """
    handles the zip uploads
    """
    return jsonify({"msg":"Closed Endpoint"})

