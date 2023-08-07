"""
Handles the operations of the endpoints
"""

import os
import sys
import re
import shutil
import time
import zipfile
import json
import datetime
import utils.trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response, session, jsonify, make_response
from flask import render_template
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging
from .extractor import Extractor
from .extractor_model import ExtractorUtil




class Util:
    """
    Handles all the api calls 
    """

    def __init__(self):
        """
        all the intializers will be handled here
        """
        
        self.secret_key = "super-scret-key" #env variable
        self.secret_salt = "secret-salt" #env variable
        self.extractor = Extractor()
        self.db_model = ExtractorUtil(self.secret_key, self.secret_salt)


    def get_operating_days(self, date, offset):
        """
        operating days calculator based on the offset
        """

        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        target_date = date - datetime.timedelta(days=int(offset))
        # Check if the target date is a working day (Monday to Friday)
        while target_date.weekday() > 5:
            target_date -= datetime.timedelta(days=1)

        return  target_date.date()

    def download_data(self):
        """
        download the data from databasse
        """

        query_strings = dict()
        query_strings['iso'] = request.form.get('iso')
        query_strings["curve_type"] = request.form.get('curve_type')
        query_strings["strip"] = request.form.getlist('strip')
        query_strings["type"] = request.form.get('type')
        query_strings["start"] = str(request.form.get('start'))
        query_strings["end"] = str(request.form.get('end'))

        if request.form.get('history'):
            query_strings['history'] = True
        else:
            query_strings['history'] = False

        query_strings["offset"] =  request.form.get('offset')
        query_strings["operating_day"] = request.form.get('operating_day')

        
        response, status= self.extract_data(query_strings)
        
        if status != "success":
            logging.error(f"{session['user']}: Unable to download the data")
            
        return response, status
         

    def extract_data(self, query_strings):
        """
        extracts the dataset from the database based on the characteristics
        """
        try:

            if ('operating_day' not in query_strings)or (query_strings['operating_day'] == ''):
                operating_day, offset = self.db_model.fetch_latest_operating_day(f"{query_strings['iso']}_{query_strings['curve_type']}")
            else:
                offset= query_strings["offset"]
                operating_day = query_strings["operating_day"]
                
            start = query_strings["start"]
            end = query_strings["end"]
            if operating_day:
                curvestart = self.get_operating_days(operating_day, offset)
                query_strings["curvestart"] = "".join(str(curvestart).split("-"))
                query_strings["curveend"] = "".join(str(operating_day).split("-"))
            else:
                query_strings["curvestart"] = None
                query_strings["curveend"] = None
                
            query_strings["start"] = "".join(str(start).split("-"))
            query_strings["end"] = "".join(str(end).split("-"))
            
            data_frame, status = self.extractor.get_custom_data(query_strings, query_strings["type"])
            file_name = f'{query_strings["curve_type"]}_{query_strings["iso"]}_{"_".join(query_strings["strip"])}_{query_strings["start"]}_{query_strings["end"]}'
            if status == "success":
                if query_strings["type"].lower()=="csv":
                    resp = Response(
                        data_frame.to_csv(),
                        mimetype="text/csv",
                        headers={"Content-disposition":
                        "attachment; filename="+file_name+".csv"}), status
                
                else:
                    
                    json_output = data_frame.to_json(orient="records", indent=4)

                    resp = Response(json_output, 
                        mimetype='application/json',
                        headers={'Content-Disposition':'attachment;filename='+file_name+'.json'}), status
                
                logging.info(f"{session['user']}: Data Extracted Successfully")
            
                    
            return resp
        except:
            resp = None, 'Unable to Fetch Data'
            return resp

