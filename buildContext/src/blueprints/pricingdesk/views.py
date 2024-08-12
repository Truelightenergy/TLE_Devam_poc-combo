import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .pricing_model import PricingDesk
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.configs import read_config
from utils.blocked_tokens import revoked_jwt

import pandas as pd


config = read_config()
price = Blueprint(config['price_desk'], __name__,
                    template_folder=config['template_path'],
                    static_folder=config['static_path'])


secret_key = config['secret_key']
secret_salt = config['secret_salt']
roles = RolesDecorator(revoked_jwt)



@price.route('/pricedeskdata', methods=['GET','POST'])
@roles.readwrite_token_required
def pricedeskdata():
    """
    Start
    """
    # return response
    # rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    # if rest_api_condition and ("acceptance" not in session):
    #     setup_session(request.headers['Authorization'].split()[-1])
    #     json_obj, status_code = api_util.upload_csv()
    #     return jsonify(json_obj), status_code
        
    # else:
    print('start')
    if request.method=="POST":
        print('working')
        # json_obj, status_code = api_util.upload_csv()
        file = request.files['file']
        if '.csv' not in file.filename:
            return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = 'File should be in csv format', message_flag = "error")
        price_request = pd.read_csv(file)
        mandatory_columns = ['Margin ($/MWh)', 'Sleeve Fee ($/MWh)', 'Utility Billing Surcharge ($/MWh)', 'Other 1 ($/MWh)', 'Other 2 ($/MWh)', 'Lookup ID4', 'Voltage', 'Utility', 'Load Profile', 'Capacity Zone', 'Load Zone', 'Curve Date', 'Start Date', 'End Date']
        if len(set(mandatory_columns)-set(price_request.columns)):
            return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = f'''"{'", "'.join(set(mandatory_columns)-set(price_request.columns))}" columns are missing''', message_flag = "error")
        iso = file.filename.split('.')[0].split('_')[-1]
        session["acceptance"]=None
        price_desk = PricingDesk()
        response, status = price_desk.calculate_price(price_request, iso)
        if status== "success":
            return response
            # return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = "Data Inserted", message_flag = "success")        
        else:    
            return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = status, message_flag = "error")
    else:
        session["acceptance"] = request.headers.get('Accept')
        return render_template('pricedesk/upload_csv.html')




@price.route('/pricedesk', methods=['GET','POST'])
@roles.readwrite_token_required
def pricedesk():
    """
    Start
    """
    # return response
    # rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    # if rest_api_condition and ("acceptance" not in session):
    #     setup_session(request.headers['Authorization'].split()[-1])
    #     json_obj, status_code = api_util.upload_csv()
    #     return jsonify(json_obj), status_code
        
    # else:
    print('start')
    if request.method=="POST":
        print('working')
        # json_obj, status_code = api_util.upload_csv()
        file = request.files['file']
        if '.csv' not in file.filename:
            return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = 'File should be in csv format', message_flag = "error")
        price_request = pd.read_csv(file)
        mandatory_columns = ['Margin ($/MWh)', 'Sleeve Fee ($/MWh)', 'Utility Billing Surcharge ($/MWh)', 'Other 1 ($/MWh)', 'Other 2 ($/MWh)', 'Lookup ID4', 'Voltage', 'Utility', 'Load Profile', 'Capacity Zone', 'Load Zone', 'Curve Date', 'Start Date', 'End Date']
        if len(set(mandatory_columns)-set(price_request.columns)):
            return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = f'''"{'", "'.join(set(mandatory_columns)-set(price_request.columns))}" columns are missing''', message_flag = "error")
        iso = file.filename.split('.')[0].split('_')[-1]
        session["acceptance"]=None
        price_desk = PricingDesk()
        response, status = price_desk.calculate_price(price_request, iso)
        if status== "success":
            return response
            # return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = "Data Inserted", message_flag = "success")        
        else:    
            return render_template('pricedesk/upload_csv.html', flash_message=True, message_toast = status, message_flag = "error")
    else:
        session["acceptance"] = request.headers.get('Accept')
        return render_template('pricedesk/upload_csv.html')