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
from .ingestor import Ingestion
from .ingestor_model import IngestorUtil



class Util:
    """
    Handles all the api calls 
    """

    def __init__(self, secret_key , secret_salt):
        """
        all the intializers will be handled here
        """
        self.UPLOAD_FOLDER = './flask_file_upload'
        self.ERROR_UPLOAD_FOLDER = './defaulted_file_upload'
        
        self.ALLOWED_EXTENSIONS = set(['zip','csv'])
        self.create_storage_folder()
        self.ingestor = Ingestion()
        self.ingestor_util = IngestorUtil(secret_key , secret_salt)


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
    
    def make_file_log(self,filename):
        """
        makes the file log for record
        """

        now = datetime.now() 
        time_stamp = now.strftime("%m/%d/%Y %H:%M:%S")

        self.ingestor_util.save_log(time_stamp, session["user"], filename)


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
                zip_ref.extractall(self.UPLOAD_FOLDER + "/unzipped/")
                zip_ref.close()
                # todo - ingestion
                return redirect(url_for('admins.upload_zip'))
        return render_template('index.html')
