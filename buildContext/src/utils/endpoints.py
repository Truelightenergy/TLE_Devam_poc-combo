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
from blueprints.ingestors.ingestor import Ingestion
from blueprints.extractors.extractor import Extractor
import utils.trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response, session, jsonify, make_response
from flask import render_template
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging
from utils.db_utils import DataBaseUtils
from blueprints.admins.admin_model import AdminUtil
from blueprints.auths.auth_model import AuthUtil
from utils.configs import read_config
config = read_config()

logging.basicConfig(level=logging.INFO)



# logs saving
logger = logging.getLogger()
# fileHandler = RotatingFileHandler("logs.log", maxBytes=1)
# logger.addHandler(fileHandler)

# logs console
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

LOG_FOLDER = './logs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logHandler = TimedRotatingFileHandler(f"{LOG_FOLDER}{config['time_log']}", when='D', interval=1)
logger.addHandler(logHandler)



class Util:
    """
    Handles all the api calls 
    """

    def __init__(self, secret_key, secret_salt):
        """
        all the intializers will be handled here
        """
        self.UPLOAD_FOLDER = config['upload_folder']
        self.ERROR_UPLOAD_FOLDER = config['defaulted_folder']
        
        self.ALLOWED_EXTENSIONS = set(['zip','csv'])
        self.create_storage_folder()
        self.ingestor = Ingestion()
        self.extractor = Extractor()
        self.admin_util = AdminUtil(secret_key, secret_salt)
        self.auth_util = AuthUtil(secret_key, secret_salt)

        

    def signup(self, email, pswd, prv_level="read_only_user"):
        """
        create user
        """           
        
        if self.validate_input(email, pswd, prv_level):
            response = self.auth_util.create_user(email, pswd, prv_level)
            if response:
                logging.info(f"User Created with email {email}")
                return {"flash_message": True, "message_toast":"User Created", "message_flag":"success"},200
            
            else:
                logging.error(f"Unable to Creat User with email {email}")
                return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},400
        else:
            logging.error(f"Unable to Creat User with email {email}")
            return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},400

    def login(self, email, pswd):
        """
        login to the application
        """
        
        # if request.method == 'POST':
        
        

        auth_flag, prv_level = self.auth_util.authenticate_user(email, pswd)
        if auth_flag:
            _, jwt_token = self.auth_util.encode_auth_token(email, pswd, prv_level)
            session["jwt_token"] = jwt_token
            session["user"] = email
            session["level"] = prv_level
            logging.info(f"{session['user']}: User Logged In SUCCESSFULLY")
            return {"msg":"Logged In Successfully", "access_token":jwt_token},200
        else:
            logging.error(f"{email}: User Logged In FAILED")
            return {"message_toast":"Login Failed", "flash_message":True, "message_flag":"error"},403

    
    def logout(self):
        """
        logout the application
        """
        logging.info(f"{session['user']}: User Logged Out")
        session["jwt_token"] = None
        session["user"] = None
        session["level"] = None
        session.clear()
        return {"msg":"User Logged Out"}, 200
    
    

    def create_storage_folder(self):
        """
        creates the upload folder 
        """
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)

        if not os.path.exists(self.ERROR_UPLOAD_FOLDER):
            os.makedirs(self.ERROR_UPLOAD_FOLDER)

           

    def allowed_file(self, filename):
        """
        allow only mentioned files format
        """
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def generate_timestamp(self):
        """
        generates the datetime
        """
        today = datetime.today()	
        timestamp = today.strftime("%d-%B-%Y %H:%M:%S")
        
        return timestamp

    def application_startup(self):
        """
        starts the application
        """
        return redirect(url_for('auths.home'))
    
    def is_valid_email(self, email):
        """
        Returns True if the given string is a valid email address, otherwise False.
        """
        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?" 
        pattern = re.compile(pattern)
        if re.match(pattern, email):
            return True
        return False


    def validate_input(self, email, pswd, prv_level):
        """
        validate user's input
        """
        levels = ['read_only_user', 'admin', 'read_write_user']
        flag = True
        if prv_level not in levels:
            flag = False
        
        if len(pswd)==0:
            flag = False
        if not self.is_valid_email(email):
            flag = False
        
        return flag

    def create_user(self, email, pswd, prv_level):
        """
        create user
        """           
        
        if self.validate_input(email, pswd, prv_level):
            response = self.auth_util.create_user(email, pswd, prv_level)
            if response:
                logging.info(f"{session['user']}: User Created with email {email}")
                return {"flash_message": True, "message_toast":"User Created", "message_flag":"success"},200
            
            else:
                logging.error(f"{session['user']}: Unable to Creat User with email {email}")
                return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},400
        else:
            logging.error(f"{session['user']}: Unable to Creat User with email {email}")
            return {"flash_message": True, "message_toast":"Unable to create user", "message_flag":"error"},400
        

    def view_user(self):
        """
        view user of applications
        """
        records = self.admin_util.get_all_users()
        return {"data":records},200
    
    def view_uploads(self):
        """
        get all the records for all file uploads
        """
        records = self.admin_util.get_all_uploads()
        return {"data":records},200
    
    def enable_disable_user(self, user_id, status):
        """
        delete user of applications
        """
        flag = self.auth_util.enable_disable_user(user_id, status)
        if flag:
            logging.info(f"{session['user']}: user {status} with User id {user_id}")
            return {"flash_message": True, "message_toast":f"User {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: user not {status} with User id {user_id}")
            return {"flash_message": True, "message_toast": f"user not {status}", "message_flag":"error"},400
        
    def enable_disable_user_from_api(self, user_email, status):
        """
        enable diable user
        """

        flag = self.auth_util.enable_disable_user_using_email(user_email, status)
        if flag:
            logging.info(f"{session['user']}: user {status} with User email {user_email}")
            return {"flash_message": True, "message_toast": f"user {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: user not {status} with User id {user_email}")
            return {"flash_message": True, "message_toast": f"user not {status}", "message_flag":"error"},400
        

    def reset_password(self, user_id):
        """
        reset user's password of applications
        """
        email = self.auth_util.get_user_email(user_id)
        if email:
            flag = self.auth_util.reset_user_password(user_id, email)
        else:
            logging.error(f"{session['user']}: Unable to Reset password for user {user_id}")
            return {"flash_message": True, "message_toast": f"Unable to Reset Password", "message_flag":"error"},400

        if flag:
            logging.info(f"{session['user']}: Password Reset for user {email}")
            return {"flash_message": True, "message_toast":f"Password Reset", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Reset password for user {email}")
            return {"flash_message": True, "message_toast": f"Unable to Reset Password", "message_flag":"error"},400
        

    def reset_password_from_api(self, email):
        """
        reset user's password from api
        """

        flag = self.auth_util.reset_user_password_for_api(email)

        if flag:
            logging.info(f"{session['user']}: Password Reset for user {email}")
            return {"flash_message": True, "message_toast":f"Password Reset", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Reset password for user {email}")
            return {"flash_message": True, "message_toast": f"Unable to Reset Password", "message_flag":"error"},400
        


    def update_user(self, user_id, prv_level):
        """
        update user of applications
        """

                   
        flag = self.admin_util.update_user(user_id, prv_level)
        records = self.admin_util.get_all_users()

        if flag:
            logging.info(f"{session['user']}: User's privileged level updated successfully with user id {user_id}")
            return {"flash_message": True, "message_toast":f"User Updated", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: Unable to Update User's privileged level with user id {user_id}")
            return {"flash_message": True, "message_toast": f"Unable to Update User", "message_flag":"error"},400
        

    def update_user_from_api(self):
        """
        update user of applications
        """
        levels = ['read_only_user', 'admin', 'read_write_user']
        if not (request.args.get("email") and request.args.get("prv_level")):
            return {"error": "Incorrect Params"}, 400
        
        email, prv_level = request.args.get('email'), request.args.get('prv_level')
        if prv_level in levels:
            flag = self.admin_util.update_user_using_email(email, prv_level)
            if flag:
                logging.info(f"{session['user']}: User's privileged level updated successfully with user email {email}")
                return {"flash_message": True, "message_toast":"User updated", "message_flag":"success"},200
            else:
                logging.error(f"{session['user']}: Unable to Update User's privileged level with user email {email}")
                return {"flash_message": True, "message_toast":"Unable to update user", "message_flag":"error"},400
        return {"flash_message": True, "message_toast":"Privileged level is not available", "message_flag":"error"},400
            


    def update_password(self, email, old_pswd, new_pswd):
        """
        update your password
        """
        
        flag = self.auth_util.update_password(old_pswd, new_pswd, email)

        if flag:
            logging.info(f"{session['user']}: User Updated his password successfully")
            return {"flash_message": True, "message_toast":"password updated", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: User Unable Updated his password")
            return {"flash_message": True, "message_toast":"unable to update password", "message_flag":"error"},400
        
        
    def remove_local_files(self, filename):
        """
        removes the files if successfully ingested from the server
        """
        source = os.path.join(self.UPLOAD_FOLDER, filename)
        if os.path.isfile(source):
            os.remove(source)
    
    def moving_defaulted_files(self, filename):
        """
        moves the file into error file folder
        """

        source = os.path.join(self.UPLOAD_FOLDER, filename)
        destination = os.path.join(self.ERROR_UPLOAD_FOLDER, filename)
        shutil.move(source, destination)
        self.remove_local_files(filename)

        
    def make_file_log(self,filename):
        """
        makes the file log for record
        """

        now = datetime.now() 
        time_stamp = now.strftime("%m/%d/%Y %H:%M:%S")

        self.admin_util.save_log(time_stamp, session["user"], filename)

    def upload_csv(self):
        """
        handles the csv upload file
        """
        
        print("/upload called", file=sys.stderr)
        print(f"POST: {request}", file=sys.stderr)
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            logging.error(f"{session['user']}: Unable to Upload file because of 'No file part'")
            # return redirect(request.url)
            return {"flash_message" : True, "message_toast" : "Unable to Upload file because of 'No file part'", "message_flag":"error"},400
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            logging.error(f"{session['user']}: Unable to Upload file because of 'No selected file'")
            return {"flash_message" : True, "message_toast" : "Unable to Upload file because of 'No selected file'", "message_flag":"error"},400
        
        
        if file and self.allowed_file(file.filename):
            print("Uploading", file=sys.stderr)
            filename = secure_filename(file.filename)
            location = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(location)
            response = self.ingestor.call_ingestor(location) # deal with result
            if response in ["Data Inserted", "Data updated"]:
                self.make_file_log(file.filename)
                self.remove_local_files(file.filename)
                logging.info(f"{session['user']}: File {file.filename} ingested successfully")
                return {"flash_message" : True, "message_toast" : "Data Inserted", "message_flag":"success"},200
            else:
                self.moving_defaulted_files(file.filename)
                logging.error(f"User: {session['user']}, File: {file.filename}, Response: {response}")
                return {"flash_message" : True, "message_toast" : response, "message_flag":"error"},400
            
        logging.info(f"{session['user']}: Unable to Upload file because of 'No selected file'")
        return {"flash_message" : True, "message_toast" : "Unable to Upload file because of 'No selected file'", "message_flag":"error"},400
            


    def upload_zip(self):
        """
        handling zip format uploads
        """

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(self.UPLOAD_FOLDER, filename))
                zip_ref = zipfile.ZipFile(os.path.join(self.UPLOAD_FOLDER, filename), 'r')
                zip_ref.extractall(self.UPLOAD_FOLDER + config['unzipped_folder'])
                zip_ref.close()
                # todo - ingestion
                return redirect(url_for('admins.upload_zip'))
        return render_template('index.html')
    
    def download_data(self):
        """
        download the data from databasse
        """

        query_strings = dict()
        query_strings['iso'] = request.form.get('iso')
        query_strings["curve_type"] = request.form.get('curve_type')
        query_strings["strip"] = request.form.getlist('strip')
        query_strings["type"] = request.form.get('type')
        start = str(request.form.get('start')).split("-")
        query_strings["start"] = "".join(start)
        if request.form.get('history'):
            query_strings['history'] = True
        else:
            query_strings['history'] = False

        end = str(request.form.get('end')).split("-")
        query_strings["end"] = "".join(end)
        
        response, status= self.extract_data(query_strings)
        
        if status != "success":
            logging.error(f"{session['user']}: Unable to download the data")
            
        return response, status
         

    def extract_data(self, query_strings):
        """
        extracts the dataset from the database based on the characteristics
        """
        try:
            data_frame, status = self.extractor.get_custom_data(query_strings, query_strings["type"])
            file_name = f'{query_strings["curve_type"]}_{query_strings["iso"]}_{"_".join(query_strings["strip"])}_{query_strings["start"]}_{query_strings["end"]}'
            if status == "success":
                if query_strings["type"]=="csv":
                    resp = Response(
                        data_frame.to_csv(),
                        mimetype="text/csv",
                        headers={"Content-disposition":
                        "attachment; filename="+file_name+".csv"}), status
                
                elif query_strings["type"]=="json":
                    resp = Response(data_frame.to_json(orient='records'), 
                        mimetype='application/json',
                        headers={'Content-Disposition':'attachment;filename='+file_name+'.json'}), status
                
                logging.info(f"{session['user']}: Data Extracted Successfully")
            else:
            
                resp = None, status
                logging.error(f"{session['user']}: Data Extraction Failed")
                    
            return resp
        except:
            resp = None, 'Unable to Fetch Data'
            return resp
    
    def app_logging(self):
        """creates logging information"""
        with open(f"{LOG_FOLDER}{config['time_log']}") as file:
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
        with open(f"{LOG_FOLDER}{config['time_log']}") as file:
            file = list(file)
            file = file[::-1]
            for i, line in enumerate(file):
                line = line.replace("", "")
                logs += line
        return logs
                

    def stream_logger(self):

        return Response(self.app_logging(), mimetype="text/plain", content_type="text/event-stream")
    
    def switch_api(self, status):
        """
        enable and disable the api side
        """
        flag = self.auth_util.switch_api(status)
        if flag:
            logging.info(f"{session['user']}: api is {status}")
            return {"flash_message": True, "message_toast":f"api is {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: api is not{status}")
            return {"flash_message": True, "message_toast": f"api is not{status}", "message_flag":"error"},400

    def switch_ui(self, status):
        """
        enable and disable the api side
        """
        flag = self.auth_util.switch_ui(status)
        if flag:
            logging.info(f"{session['user']}: ui is {status}")
            return {"flash_message": True, "message_toast":f"ui is {status}", "message_flag":"success"},200
        else:
            logging.error(f"{session['user']}: ui is not{status}")
            return {"flash_message": True, "message_toast": f"ui is not{status}", "message_flag":"error"},400
        
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
            return {"flash_message": True, "message_toast": f"Unable to Remove column Authentication", "message_flag":"error"},400
        
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
        
        
        flag = self.admin_util.check_filter_rule(query_strings)
        if flag:
            flag = self.admin_util.ingest_filter_rule(query_strings)
        
        if flag:
            logging.info(f"{session['user']}: Filter Rule Added Successfully")
            return {"flash_message": True, "message_toast":f"Filter Rule Added Successfully"},200
        else:
            logging.error(f"{session['user']}: Unable to Add Filter Rule")
            return {"flash_message": True, "message_toast": f"Unable to Add Filter Rule", "message_flag":"error"},400
        
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
            return {"flash_message": True, "message_toast":f"Filter Rule Added Successfully"},200
        else:
            logging.error(f"{session['user']}: Unable to Add Filter Rule")
            return {"flash_message": True, "message_toast": f"Unable to Add Filter Rule", "message_flag":"error"},400
        
            
        