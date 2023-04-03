import os
from endpoints_util import Util
from flask import Flask, request, render_template



api_util = Util()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = api_util.UPLOAD_FOLDER



# figure out how to get with curl as well
@app.route('/upload_csv', methods=['GET','POST'])
def upload_csv():
    """
    handles the csv file uploads
    """
    response = api_util.upload_csv()
    return response

@app.route('/', methods=['GET'])
def index():
    """
    start up aplications
    """
    response = api_util.application_startup()
    return response


@app.route('/upload_zip', methods=['GET','POST'])
def upload_zip():
    """
    handles the zip uploads
    """
    response = api_util.upload_zip()
    return response

@app.route('/get_data', methods=['GET','POST'])
def get_data():
    """
    Extracts the data based on the query strings
    """
    args = request.args.to_dict()
    response, status = api_util.extract_data(args)
    if status != "success":
        return status
    return response


@app.route('/download_data', methods=['GET','POST'])
def download_data():
    """
    handles data downloads
    """
    response = api_util.download_data()
    return response

@app.errorhandler(Exception)          
def error_handler(e):
    return api_util.custom_error_handler(e)          
    



if __name__ == "__main__":
    print("Starting")
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(port=5555)
