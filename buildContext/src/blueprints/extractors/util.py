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
from io import BytesIO
from io import StringIO
import pandas as pd
import datetime
import utils.trueprice_database as tpdb
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, flash, render_template, Response, session, jsonify, make_response
from flask import render_template
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import logging
from .extractor import Extractor
from .extractor_model import ExtractorUtil
from utils.configs import read_config



config = read_config()
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

        if  'history' not in request.form:
            query_strings['history'] = False
        
        elif request.form.get('history').lower()=='all':
            query_strings['history'] = True

        else:
            query_strings['history'] = False
            query_strings['cob'] = True

        query_strings["offset"] =  0
        query_strings["operating_day"] = request.form.get('operating_day')
        query_strings["operating_day_end"] = request.form.get('operating_day_end')

        
        response, status= self.extract_data(query_strings)
        
        if status != "success":
            logging.error(f"{session['user']}: Unable to download the data")
            
        return response, status
         
    def pd_str_to_excel(self, data_frame):
        """
        converts the dataframe to excel
        """
        data_frame = pd.read_csv(StringIO(data_frame), header = None)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data_frame.to_excel(writer, sheet_name='Sheet1', index=False, header=False)

        output.seek(0)
        return output
    
    def get_csv_string_with_disclaimer(self,csv_string):
        """
        Converts a DataFrame to a CSV string and appends a disclaimer.
        """
        disclaimer_text = (
        '\r\n"The information in this file is intended only for the use of authorized '
        'clients of TRUELight Energy\'s TRUEPrice products & services. If you are '
        'not the intended recipient of this file, or the person responsible for '
        'delivering this file to the intended recipient, you are strictly prohibited '
        'from disclosing, copying, distributing, or retaining this file or any part '
        'of it. This file contains information which is confidential and covered by '
        'legal, professional, or other privileges under applicable law. If you have '
        'received this file in error, please notify TRUELight by email at '
        'info@truelightenergy.com"\r\n'
        )
    
        # Append the disclaimer to the CSV string
        csv_string_with_disclaimer = csv_string + disclaimer_text
        
        return csv_string_with_disclaimer

    def extract_data(self, query_strings):
        """
        extracts the dataset from the database based on the characteristics
        """
        try:

            if ('operating_day' not in query_strings)or (query_strings['operating_day'] == ''):
                operating_day, offset = self.db_model.fetch_latest_operating_day(f"{query_strings['iso']}_{query_strings['curve_type']}")
                operating_day_end = operating_day
            else:
                offset= query_strings["offset"]
                operating_day = query_strings["operating_day"]
                operating_day_end = query_strings["operating_day_end"]
                
            start = query_strings["start"]
            end = query_strings["end"]
            if operating_day:
                curvestart = self.get_operating_days(operating_day, offset)
                query_strings["curvestart"] = "".join(str(curvestart).split("-"))
                query_strings["curveend"] = "".join(str(operating_day_end).split("-"))
            else:
                query_strings["curvestart"] = None
                query_strings["curveend"] = None
                
            query_strings["start"] = "".join(str(start).split("-"))
            query_strings["end"] = "".join(str(end).split("-"))
            
            data_frame, status = self.extractor.get_custom_data(query_strings, query_strings["type"])
            cleaned_strings = [s.replace("strip_", "") for s in query_strings["strip"]]
            file_name = f'{query_strings["curve_type"]}_{query_strings["iso"]}_{"_".join(cleaned_strings)}_{operating_day}'
            if data_frame.empty:
                return data_frame, "No Such Data Available"
            
            if status == "success":
                if query_strings["type"].lower()=="xlsx":

                    if (query_strings["curve_type"]).lower() == 'matrix':
                        data = self.get_csv_string_with_disclaimer(data_frame.to_csv(header=None))
                        data = self.pd_str_to_excel(data)
                        resp = Response(
                        data,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            headers={"Content-disposition":
                            "attachment; filename="+file_name+".xlsx"}), status
                    elif(query_strings["curve_type"]).lower() == 'headroom':
                        data = self.get_csv_string_with_disclaimer(data_frame.to_csv(index=False))
                        data = self.pd_str_to_excel(data)
                        resp = Response(
                        data,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            headers={"Content-disposition":
                            "attachment; filename="+file_name+".xlsx"}), status
                    else:
                        data = self.get_csv_string_with_disclaimer(data_frame.to_csv())
                        data = self.pd_str_to_excel(data)
                        resp = Response(
                            data,
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            headers={"Content-disposition":
                            "attachment; filename="+file_name+".xlsx"}), status
                        
                elif query_strings["type"].lower()=="csv":

                    if (query_strings["curve_type"]).lower() == 'matrix':
                        data = self.get_csv_string_with_disclaimer(data_frame.to_csv(header=None))
                        resp = Response(
                        data,
                        mimetype="text/csv",
                        headers={"Content-disposition":
                        "attachment; filename="+file_name+".csv"}), status
                    elif(query_strings["curve_type"]).lower() == 'headroom':
                        data = self.get_csv_string_with_disclaimer(data_frame.to_csv(index=False))
                        resp = Response(
                        data,
                        mimetype="text/csv",
                        headers={"Content-disposition":
                        "attachment; filename="+file_name+".csv"}), status
                    else:
                        data = self.get_csv_string_with_disclaimer(data_frame.to_csv())
                        resp = Response(
                            data,
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
            return None, status 
            
        except Exception as e:
            # Print the error to console
            # print("An error occurred while adding the disclaimer:", e, file=sys.stderr)
            resp = None, 'Unable to Fetch Data'
            return resp
        
    def extract_operating_day(self, curve, iso):
        """
        extracts the operating days
        """

        return self.db_model.get_all_operating_days(curve, iso)
    
    def extract_operating_day_with_load_zone(self, table, load_zone):
        """
        extracts the operating days with load_zone
        """

        return self.db_model.get_all_operating_days_with_load_zone(table, load_zone)
    
    def cob_availability_check(self, table, date):
        """
        finds the availability check for cob
        """
        return self.db_model.cob_availability(table, date)
        


