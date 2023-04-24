"""
Handles the operations of the endpoints
"""

import os
import sys
import time
import zipfile
from datetime import datetime
from ingestors.ingestor import Ingestion
from extractors.extractor import Extractor
import trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response, session, jsonify
from flask import render_template
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging
from auths import Auths




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

logHandler = TimedRotatingFileHandler(f"{LOG_FOLDER}/time_log.log", when='H', interval=1)
logger.addHandler(logHandler)



class Util:
    """
    Handles all the api calls 
    """

    def __init__(self, secret_key, secret_salt):
        """
        all the intializers will be handled here
        """
        self.UPLOAD_FOLDER = './flask_file_upload'
        self.ALLOWED_EXTENSIONS = set(['zip','csv'])
        self.create_storage_folder()
        self.ingestor = Ingestion()
        self.extractor = Extractor()
        self.auth_obj = Auths(secret_key, secret_salt)

    def login(self):
        """
        login to the application
        """

        # email, pswd = "ali.haider@techliance.com", "admin"
        # email, pswd = "ali.haider@gmail.com", "notadmin"

        if request.method == 'POST':
            email = request.form.get('email')
            pswd = request.form.get('password')

            auth_flag, prv_level = self.auth_obj.authenticate_user(email, pswd)
            if auth_flag:
                _, jwt_token = self.auth_obj.encode_auth_token(email, pswd)
                session["jwt_token"] = jwt_token
                session["user"] = email
                session["level"] = prv_level
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "User Logged In", msg = "Success", committer = session["user"])
                return self.application_startup()
            else:
                return render_template('login.html',  flash_message=True, message_toast = "Login Failed", message_flag = "error", page_type = "download")

        return render_template('login.html')
    
    def logout(self):
        """
        logout the application
        """
        self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "User Logged Out", msg = "Success", committer = session["user"])
        session["jwt_token"] = None
        session["user"] = None
        session["level"] = None
        session.clear()
        return redirect(url_for("login"))
    

    def create_storage_folder(self):
        """
        creates the upload folder 
        """
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)

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
        starts the
        """
        return render_template("index.html")
    
    def save_logs(self, timestamp =None, ip = None, req_method = None, action = None, msg=None, committer=None):
        """
        save the logs hourly based on the file
        """

        current_log = ""
        if timestamp:
            current_log = f"TimStamp: {self.generate_timestamp()}"
        if ip:    
            current_log = f"{current_log} | Ip: {ip}" 
        if req_method:
             current_log = f"{current_log} | Method: {req_method}" 
        if action:
            current_log = f"{current_log} | Action: {action}"
        if msg:
            current_log = f"{current_log} | Action: {action} | Msg: {msg}"
        if committer:
            current_log = f"{current_log} | Action: {action} | Committed by: {committer}"

        logger.error(f"\n{current_log}\n")


    def create_user(self):
        """
        create user
        """
        # email, pswd, prv_level ="ali.haider@techliance.com", "admin", "admin"
        # response = self.auth_obj.create_user(email, pswd, prv_level)
        # print(response)


        if request.method=="POST":
            prv_level= request.form.get('prv_level')            
            email = request.form.get("email")
            pswd = request.form.get("password")

            response = self.auth_obj.create_user(email, pswd, prv_level)
            if response:
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "User Creation", msg = "User Created", committer = session["user"])
                return render_template('create_user.html', flash_message=True, message_toast = "User Created", message_flag = "success", page_type = "download")
            
            else:
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "User Creation", msg = "Unable to Create user", committer = session["user"])
                return render_template('create_user.html', flash_message=True, message_toast = "Unable to create user", message_flag = "error", page_type = "download")


        return render_template("create_user.html")


    def upload_csv(self):
        """
        handles the csv upload file
        """
        
        print("/upload called", file=sys.stderr)
        if request.method == 'POST':
            print(f"POST: {request}", file=sys.stderr)
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "Data Ingestion", msg = "No file part", committer = session["user"])
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "Data Ingestion", msg = "No selected file", committer = session["user"])
                return redirect(request.url)
            if file and self.allowed_file(file.filename):
                print("Uploading", file=sys.stderr)
                filename = secure_filename(file.filename)
                location = os.path.join(self.UPLOAD_FOLDER, filename)
                file.save(location)
                response = self.ingestor.call_ingestor(location) # deal with result
                if response == "Data Inserted":
                    flag = "success"  
                else:
                    if len(response)>100:
                        response = "Some Error Occurred While File Upload"
                    flag = "error"
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "File Ingestion", msg = response, committer = session["user"])
                
                return render_template('upload_csv.html', flash_message=True, message_toast = response, message_flag = flag, page_type = "upload")
                # return redirect(url_for('upload_csv')
        
        return render_template("upload_csv.html")

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
                zip_ref.extractall(self.UPLOAD_FOLDER + "/unzipped/")
                zip_ref.close()
                # todo - ingestion
                return redirect(url_for('upload_zip'))
        return render_template('index.html')
    
    def download_data(self):
        """
        download the data from databasse
        """
        if request.method == 'POST':
            query_strings = dict()
            query_strings['iso'] = request.form.get('iso')
            query_strings["curve_type"] = request.form.get('curve_type')
            query_strings["strip"] = request.form.get('strip').split("_")[-1]
            query_strings["type"] = request.form.get('type')
            start = str(request.form.get('start')).split("-")
            query_strings["start"] = "".join(start)

            end = str(request.form.get('end')).split("-")
            query_strings["end"] = "".join(end)
            
            response, status = self.extract_data(query_strings)
            
            if status != "success":
                return render_template('download_data.html',  flash_message=True, message_toast = status, message_flag = "error", page_type = "download")
            else:
                
                return response
        return render_template('download_data.html')
         

    def extract_data(self, query_strings):
        """
        extracts the dataset from the database based on the characteristics
        """

        data_frame, status = self.extractor.get_custom_data(query_strings)
        file_name = f'{query_strings["curve_type"]}_{query_strings["iso"]}_{query_strings["strip"]}_{query_strings["start"]}_{query_strings["end"]}'
        if status == "success":
            if query_strings["type"]=="csv":
                resp = Response(
                    data_frame.to_csv(index=False),
                    mimetype="text/csv",
                    headers={"Content-disposition":
                    "attachment; filename="+file_name+".csv"}), status
            
            elif query_strings["type"]=="json":
                resp = Response(data_frame.to_json(orient="records"), 
                    mimetype='application/json',
                    headers={'Content-Disposition':'attachment;filename='+file_name+'.json'}), status
            
            
        else:
        
            resp = None, 'Unable to Fetch Data'
        self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "Data Extraction", msg = resp[1], committer = session["user"])
                
        return resp
    
    def app_logging(self):
        """creates logging information"""
        with open(f"{LOG_FOLDER}/time_log.log") as file:
            for line in file:
                line = line.replace("", "")
                logs = line + "\n"
                yield logs.encode()
                time.sleep(0.3)

    def stream_logger(self):

        return Response(self.app_logging(), mimetype="text/plain", content_type="text/event-stream")


    
