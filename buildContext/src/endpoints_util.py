"""
Handles the operations of the endpoints
"""

import os
import sys
import zipfile
from datetime import datetime
from ingestors.ingestor import Ingestion
from extractors.extractor import Extractor
import trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response
from flask import render_template
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging

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

logHandler = TimedRotatingFileHandler(f'{LOG_FOLDER}/logs.log', when='H', interval=1)
logger.addHandler(logHandler)



class Util:
    """
    Handles all the api calls 
    """

    def __init__(self):
        """
        all the intializers will be handled here
        """
        self.UPLOAD_FOLDER = './flask_file_upload'
        self.ALLOWED_EXTENSIONS = set(['zip','csv'])
        self.create_storage_folder()
        self.ingestor = Ingestion()
        self.extractor = Extractor()

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
    
    def save_logs(self, timestamp =None, ip = None, req_method = None, action = None, msg=None):
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

        logger.error(f"\n{current_log}\n")



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
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "Data Ingestion", msg = "No file part")
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "Data Ingestion", msg = "No selected file")
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
                self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "File Ingestion", msg = response)
                
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
        self.save_logs(timestamp= self.generate_timestamp(), ip= request.environ['REMOTE_ADDR'], req_method = request.method, action = "Data Extraction", msg = resp[1])
                
        return resp
