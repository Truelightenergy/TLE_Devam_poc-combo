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
from .extractor import Extractor




class Util:
    """
    Handles all the api calls 
    """

    def __init__(self):
        """
        all the intializers will be handled here
        """
        
        self.extractor = Extractor()

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

