"""
Handles the operations of the endpoints
"""

import os
import sys
import zipfile
from ingestors.ingestor import Ingestion
from extractors.extractor import Extractor
import trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response

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

    def application_startup(self):
        """
        starts the
        """
        return "<p>The new TRUEPrice API, see /upload or /zip or /get_data</p>"

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
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and self.allowed_file(file.filename):
                print("Uploading", file=sys.stderr)
                filename = secure_filename(file.filename)
                location = os.path.join(self.UPLOAD_FOLDER, filename)
                file.save(location)
                self.ingestor.call_ingestor(location) # deal with result
                return redirect(url_for('upload_csv'))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''

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

    def extract_data(self, query_strings):
        """
        extracts the dataset from the database based on the characteristics
        """
        data_frame, status = self.extractor.get_custom_data(query_strings)
        file_name = f'{query_strings["curve_type"]}_{query_strings["iso"]}_{query_strings["strip"]}_{query_strings["start"]}_{query_strings["end"]}'
        if status == "success":
            if query_strings["type"]=="csv":
                return Response(
                    data_frame.to_csv(index=False),
                    mimetype="text/csv",
                    headers={"Content-disposition":
                    "attachment; filename="+file_name+".csv"})
            
            elif query_strings["type"]=="json":
                return Response(data_frame.to_json(orient="records"), 
                    mimetype='application/json',
                    headers={'Content-Disposition':'attachment;filename='+file_name+'.json'})
            
        else:
            return f'<h1>{status}</h1>'