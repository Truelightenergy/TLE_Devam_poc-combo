"""
Handles the operations of the endpoints
"""

import os
import sys
import re
import shutil
import time
import zipfile
from datetime import datetime
import utils.trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response, session, jsonify, make_response
from flask import render_template
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging
from .admin_model import AdminUtil
from utils.configs import read_config


config = read_config()

LOG_FOLDER = config['logging_folder']
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)





class Util:
    """
    Handles all the api calls 
    """

    def __init__(self):
        """
        all the intializers will be handled here
        """
        self.secret_key = config['secret_key']
        self.secret_salt = config['secret_salt']
        self.admin_util = AdminUtil(self.secret_key, self.secret_salt)

    def stream_logger(self):
        return Response(self.app_logging(), mimetype="text/plain", content_type="text/event-stream")
    

    def app_logging(self):
        """creates logging information"""
        with open(f"{LOG_FOLDER}/time_log.log") as file:
            file = list(file)
            file = file[::-1]
            for line in file:
                line = line.replace("", "")
                logs = line
                yield logs.encode()
                time.sleep(0.3)

    def app_logging_api(self):
        """creates logging information"""
        logs = ""
        with open(f"{LOG_FOLDER}/time_log.log") as file:
            file = list(file)
            file = file[::-1]
            for i, line in enumerate(file):
                line = line.replace("", "")
                logs += line
        return logs
    
    def view_uploads(self):
        """
        get all the records for all file uploads
        """
        records = self.admin_util.get_all_uploads()
        return {"data":records},200
    
    def switch_ui(self, status):
        """
        enable and disable the api side
        """
        flag = self.admin_util.switch_ui(status)
        if flag:
            logging.info(f"{session['user']}: ui is {status}")
            return {"flash_message": True, "message_toast":f"ui is {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: ui is not{status}")
            return {"flash_message": True, "message_toast": f"ui is not{status}", "message_flag":"error"},200
  
    def switch_api(self, status):
        """
        enable and disable the api side
        """
        flag = self.admin_util.switch_api(status)
        if flag:
            logging.info(f"{session['user']}: api is {status}")
            return {"flash_message": True, "message_toast":f"api is {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: api is not{status}")
            return {"flash_message": True, "message_toast": f"api is not{status}", "message_flag":"error"},200

    def get_column_filter_for_user_from_api(self, email):
        """
        get all filters of columns for every user
        """
        try:
            response = self.admin_util.view_authorized_columns_from_api(email)
            status_code = 200
        except:
                response = None
                status_code =400
        return response, status_code
        

    def get_column_filter_for_user(self, user_id):
        """
        get all filters of columns for every user
        """
        try:
            response = self.admin_util.view_authorized_columns_from_ui(user_id)

            status_code = 200
        except:
                response = None
                status_code =400
        return response, status_code
    
    def remove_all_subscription(self, user_id):
        """
        removes all the subscriptions
        """
        try:
            response = self.admin_util.remove_all_subscription(user_id)
            status_code = 200
        except:
            response = None
            status_code = 400
        return response, status_code
    
    def remove_column_auth_filter(self, filter_id):
        """
        enable and disable the api side
        """
        flag = self.admin_util.delete_auth_column_filter(filter_id)
        if flag:
            logging.info(f"{session['user']}: Authentication Removed on columns")
            return {"flash_message": True, "message_toast":f" Authentication Removed on columns", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Remove column Authentication")
            return {"flash_message": True, "message_toast": f"Unable to Remove column Authentication", "message_flag":"error"},200
        
    def add_filter_ui(self):
        """
        add new filter to the columns for each user
        """

        query_strings = dict()
        query_strings['user'] = request.form.get('user')
        query_strings["control_table"] = request.form.get('control_table')
        query_strings["control_area"] = request.form.get('control_area')
        query_strings["state"] = request.form.get('state')
        query_strings['load_zone'] = request.form.get('load_zone')
        query_strings["capacity_zone"] = request.form.get('capacity_zone')
        query_strings["utility"] = request.form.get('utility')
        query_strings["strip"] = request.form.get('strip')
        query_strings['cost_group'] = request.form.get('cost_group')
        query_strings["cost_component"] = request.form.get('cost_component')
        query_strings["sub_cost_component"] = request.form.get('sub_cost_component')
        query_strings["start"] = request.form.get('start')
        query_strings["end"] = request.form.get('end')
        query_strings["balanced_month"] = request.form.get('bal_month')
        
        
        flag = self.admin_util.remove_previous_filter_rule(query_strings)
        if flag:
            flag = self.admin_util.ingest_filter_rule(query_strings)
        
        if flag:
            logging.info(f"{session['user']}: Filter Rule Added Successfully")
            return {"flash_message": True, "message_toast":f"Filter Rule Added Successfully", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Add Filter Rule")
            return {"flash_message": True, "message_toast": f"Unable to Add Filter Rule", "message_flag":"error"},200
        
    def add_filter_api(self):
        """
        add new filter to the columns for each user
        """

        query_strings = dict()
        query_strings['user'] = request.args.get('user')
        query_strings["control_table"] = request.args.get('control_table')
        query_strings["control_area"] = request.args.get('control_area')
        query_strings["state"] = request.args.get('state')
        query_strings['load_zone'] = request.args.get('load_zone')
        query_strings["capacity_zone"] = request.args.get('capacity_zone')
        query_strings["utility"] = request.args.get('utility')
        query_strings["strip"] = request.args.get('strip')
        query_strings['cost_group'] = request.args.get('cost_group')
        query_strings["cost_component"] = request.args.get('cost_component')
        query_strings["sub_cost_component"] = request.args.get('sub_cost_component')
        query_strings["start"] = request.args.get('start')
        query_strings["end"] = request.args.get('end')      
        
        flag = self.admin_util.check_filter_rule(query_strings)
        if flag:
            flag = self.admin_util.ingest_filter_rule(query_strings)
        
        if flag:
            logging.info(f"{session['user']}: Filter Rule Added Successfully")
            return {"flash_message": True, "message_toast":f"Filter Rule Added Successfully", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Add Filter Rule")
            return {"flash_message": True, "message_toast": f"Unable to Add Filter Rule", "message_flag":"error"},200
        
    def multiple_filters_ingestion(self):
        """
        add multiple filters at once
        """

        try:

            data = request.get_json()
            filters= self.pre_processing_data(data)
            flag = self.admin_util.ingest_multiple_filters(filters, data["email"])
            if flag:
                logging.info(f"{session['user']}: Filter Rule Added Successfully")
                return {"flash_message": True, "message_toast":f"Filter Rules Added Successfully", "message_flag":"success"},200
            else:
                logging.error(f"{session['user']}: Unable to Add Filter Rule")
                return {"flash_message": True, "message_toast": f"Unable to Add Filter Rules", "message_flag":"error"},200
        except:
            logging.error(f"{session['user']}: Unable to Add Filter Rule")
            return {"flash_message": True, "message_toast": f"Unable to Add Filter Rules", "message_flag":"error"},400
            
    def pre_processing_data(self, data):
        """
        makes data ready for bulk ingestions
        """      
        filtered_data = data["data"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        email = data["email"]
        bal_month = data["balanced_month"]

        filters = list()

        for curve in filtered_data:
            if curve is None:
                continue
            for control_area in filtered_data[curve]:
                if control_area is None:
                    continue
                control_table = f"{control_area}_{curve}"
                catalog_data = filtered_data[curve][control_area]
                for item in catalog_data:
                    if item is None:
                        continue
                    item["control_table"] = control_table
                    item["start"] = start_date
                    item["end"] = end_date
                    item['user'] = email
                    item['balanced_month'] = bal_month
                    filters.append(item)
        return filters

        
    