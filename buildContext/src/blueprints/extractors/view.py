import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .util import Util
from .extractor_model import ExtractorUtil
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.keys import secret_key, secret_salt
from utils.blocked_tokens import revoked_jwt


extractors = Blueprint('extractors', __name__,
                    template_folder="../templates/",
                    static_folder='static')




db_obj = ExtractorUtil(secret_key, secret_salt)
api_util = Util()
roles = RolesDecorator(revoked_jwt)




def setup_session(auth_token):
    """
    setup the session for the api requests
    """

    payload = db_obj.decode_auth_token(auth_token)[1]
    session["jwt_token"] = auth_token
    session["user"] = payload["client_email"]
    session["level"] = payload["role"]


@extractors.route('/download_data', methods=['GET','POST'])
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
                return render_template('extractors/download_data.html',  flash_message=True, message_toast = status, message_flag = "error")
            return response
        else:
            return render_template('extractors/download_data.html')
        
@extractors.route('/get_data', methods=['GET','POST'])
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
        description: data downloaded successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to download data
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

        

