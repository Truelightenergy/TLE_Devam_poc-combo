import os
from datetime import datetime
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .util import Util
from .extractor_model import ExtractorUtil
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.configs import read_config
from utils.blocked_tokens import revoked_jwt


config =  read_config()


extractors = Blueprint(config['extractors_path'], __name__,
                    template_folder=config['template_path'],
                    static_folder=config['static_path'])


secret_key = config['secret_key']
secret_salt = config['secret_salt']

db_obj = ExtractorUtil(secret_key, secret_salt)
api_util = Util()
roles = RolesDecorator(revoked_jwt)

def sort_dates(dates_lst):
    '''
    sorts the date according to the list
    '''

    date_strings = ['2023-11-10', '2023-08-15', '2024-01-01', '2023-05-20']

    # Convert the strings to datetime objects
    date_objects = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in dates_lst]

    # Sort the datetime objects in descending order
    sorted_dates = sorted(date_objects, reverse=True)

    # Convert the sorted datetime objects back to string format if needed
    sorted_date_strings = [date.strftime('%Y-%m-%d') for date in sorted_dates]

    return sorted_date_strings





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
        description: yyyy-mm-dd
    
      - name: end
        in: query
        type: string
        format: date
        required: true
        description: yyyy-mm-dd

      - name: operating_day
        in: query
        type: string
        format: date
        required: false
        description: yyyy-mm-dd

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
        type:  string
        required: true
        description: cob or all

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
    if request.args.get('history').lower()=="all":
        args['history'] = True
    else:
        args['history'] = False

    response, status = api_util.extract_data(args)
    if status != "success":
        return status
    return response


@extractors.route('/get_options_for_strips', methods=['GET', 'POST'])
@roles.readonly_token_required
def get_options_for_strips():

    """
    makes the current drop down dynamic
    """
    curve = request.json['curve']
    if curve.lower() in ("nonenergy", "all"):
        option = ["7x24","5x16", "7x8", "2x16", "WD", "WE"]
    elif curve.lower() == "energy":
        option = ["7x24", "5x16", "7x8", "2x16"]
    else:
        option = ['7x24']
    return jsonify(option)

@extractors.route('/get_options', methods=['GET', 'POST'])
@roles.readonly_token_required
def get_options():

    """
    makes the current drop down dynamic
    """
    curve = request.json['curve']
    if curve == "rec":
        option = ["ERCOT", "ISONE", "NYISO", "PJM", "ALL"]
    else:
        option = ["ERCOT", "ISONE", "NYISO","MISO", "PJM", "ALL"]
    return jsonify(option)

@extractors.route('/get_operating_day', methods=['GET', 'POST'])
@roles.readonly_token_required
def get_operating_day():

    """
    fetches the relevant curve's operating days
    """

    curve = request.json['curve']
    iso = request.json['iso']
    operating_days = api_util.extract_operating_day(curve, iso)
    operating_days = sort_dates(operating_days)
    return jsonify(operating_days)

@extractors.route('/cob_check', methods=['GET', 'POST'])
@roles.readonly_token_required
def cob_check():

    """
    fetches the relevant curve's operating days
    """
    curve = request.json['curve']
    iso = request.json['iso']
    flag = False
    if curve.lower() in ('energy', 'all'):
      flag=api_util.cob_availability_check(iso, request.json['operating_day'], request.json['operating_day_end'])
    return jsonify(flag)

@extractors.route('/get_operating_days', methods=['GET', 'POST'])
@roles.readonly_token_required
def get_operating_days():

    """
    fetches the relevant curve's operating days
    """
    table = request.json['table']
    load_zone = request.json['load_zone']
    operating_days = api_util.extract_operating_day_with_load_zone(table, load_zone)
    operating_days = sort_dates(operating_days)
    return jsonify(operating_days)
    

@extractors.route('/intraday_timestamps_download', methods=['GET', 'POST'])
@roles.readonly_token_required
def intraday_timestamps_download():
    """
    returns the intraday timestamps
    """
    curve = request.json.get('curve')
    iso = request.json.get('iso')
    operating_day_start = request.json.get("operating_day_start")
    operating_day_end = request.json.get("operating_day_end")
    timestamps = api_util.intraday_timestamps_download(curve, iso, operating_day_start, operating_day_end)
    return jsonify(timestamps)