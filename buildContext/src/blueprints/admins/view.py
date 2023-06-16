import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .util import Util
from .admin_model import AdminUtil
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.keys import secret_key, secret_salt
from utils.blocked_tokens import revoked_jwt


admins = Blueprint('admins', __name__,
                    template_folder="../templates/",
                    static_folder='static')





db_obj = AdminUtil(secret_key, secret_salt)
api_util = Util()
roles = RolesDecorator(revoked_jwt)



def setup_session(auth_token):
    """
    setup the session for the api requests
    """

    payload = db_obj.decode_auth_token(auth_token)[1]
    session["jwt_token"] = auth_token
    session["user"] = payload["client_email"]
    session["level"] = payload["role"]

@admins.route('/get_options', methods=['GET', 'POST'])
@roles.readonly_token_required
def get_options():

    """
    makes the current drop down dynamic
    """
    curve = request.json['curve']
    if curve=="energy":
        option = ["ERCOT", "ISONE", "NYISO","MISO", "PJM"]
    elif curve == "nonenergy":
        option = ["ERCOT", "ISONE", "NYISO","MISO", "PJM"]
    elif curve == "rec":
        option = ["ERCOT", "ISONE", "NYISO", "PJM"]

    return jsonify(option)

@admins.route("/log_stream", methods=['GET','POST'])
@roles.admin_token_required
def log_stream():
    """returns logging information"""
    return api_util.stream_logger()

@admins.route("/get_logs", methods=['GET','POST'])
@roles.admin_token_required
def get_logs():
    """
    Logs of the application.
    ---
    tags:
      - Logs
    security:
        - Bearer: []
    responses:
      200:
        description: Getting Logs successful
      302:
        description: Unable to get Logs
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        json_obj = api_util.app_logging_api()
        return json_obj,200
    else:
        return render_template("admins/log_streaming.html")  

@admins.route('/upload_status', methods=['GET', 'POST'])
@roles.readonly_token_required
def upload_status():
    """
    get recent uploads
    ---
    tags:
      - Recent Uploads
    security:
        - Bearer: []
    responses:
      200:
        description: Uploads status
      302:
        description: Failed
    """
    
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        return jsonify(db_obj.get_all_uploads_data()),200
    else:
        json_obj, status_code  = api_util.view_uploads()
        return render_template("admins/upload_status.html", data = json_obj["data"])   
    

@admins.route('/maintainance', methods=['GET', 'POST'])
def maintainance():
    """
    view all uploads of applications 
    """
    return render_template("maintainance.html")


# application endpoint
@admins.route('/enable_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_ui():
    """
    Enable UI
    ---
    tags:
      - Enable UI
    security:
        - Bearer: []
    responses:
      200:
        description: UI Disabled successful
      302:
        description: Unable to disable UI
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_ui("enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_ui("enabled")
        record = db_obj.get_site_controls()
        if status_code==200:
            return render_template('admins/site_control.html', flash_message=True, message_toast = "UI enabled", message_flag = "success", data=record)
        return render_template('admins/site_control.html', flash_message=True, message_toast = "Unable to enable UI", message_flag = "error", data=record)


@admins.route('/disable_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_ui():
    """
    Disable UI
    ---
    tags:
      - Disable UI
    security:
        - Bearer: []
    responses:
      200:
        description: UI Disabled successful
      302:
        description: Unable to disable UI
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_ui("disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_ui("disabled")
        record = db_obj.get_site_controls()
        if status_code==200:
            return render_template('admins/site_control.html', flash_message=True, message_toast = "UI disabled", message_flag = "success",data=record)
        return render_template('admins/site_control.html', flash_message=True, message_toast = "Unable to disable UI", message_flag = "error", data=record)

# application endpoint
@admins.route('/enable_api', methods=['GET', 'POST'])
@roles.admin_token_required
def enable_api():
    """
    ENable API
    ---
    tags:
      - Enable API
    security:
        - Bearer: []
    responses:
      200:
        description: API Enable successful
      302:
        description: Unable to Enable API
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_api("enabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_api("enabled")
        record = db_obj.get_site_controls()
        if status_code==200:
          return render_template('admins/site_control.html', flash_message=True, message_toast = "API Enabled", message_flag = "success", data=record)
        return render_template('admins/site_control.html', flash_message=True, message_toast = "Unable to enable API", message_flag = "error", data=record)


@admins.route('/disable_api', methods=['GET', 'POST'])
@roles.admin_token_required
def disable_api():
    """
    Disable API
    ---
    tags:
      - Disable API
    security:
        - Bearer: []
    responses:
      200:
        description: API Disabled successful
      302:
        description: Unable to disable API
    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.switch_api("disabled")
        return jsonify(json_obj), status_code
    else:
        
        json_obj, status_code = api_util.switch_api("disabled")
        record = db_obj.get_site_controls()
        if status_code==200:
          return render_template('admins/site_control.html', flash_message=True, message_toast = "API disable", message_flag = "success",data=record)
        return render_template('admins/site_control.html', flash_message=True, message_toast = "Unable to disable API", message_flag = "error", data=record)


@admins.route('/site_control', methods=['GET', 'POST'])
@roles.admin_token_required
def site_control():
    """
    Site Control of the application.
    ---
    tags:
      - Site Control
    security:
        - Bearer: []
    responses:
      200:
        description: Getting site controls successful
      302:
        description: Unable to get site controls
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        return jsonify(db_obj.get_site_controls_data()),200
        
    else:
        record = db_obj.get_site_controls()
        return render_template("admins/site_control.html", data = record)
    

# application endpoint
@admins.route('/view_authorized_columns_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def view_authorized_columns_ui():
    """
    View Column Filter for a user
     
    ---
    tags:
      - Users - Column Filter
    security:
        - Bearer: []
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
        description: User Id to reset its password
    responses:
      200:
        description: authorized columns view
      400:
        description: authorized columns not view
      403:
        description: Something went wrong
    """

    user_id = request.args.get('user_id')
    if not user_id:
        record = db_obj.get_all_users()
        return render_template('auths/view_user.html', data=record)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("user_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.get_column_filter_for_user(user_id)
        return jsonify(json_obj), status_code
    else:
        
        record = db_obj.get_user_authorized_columns(user_id)
        return render_template('admins/view_filtered_columns.html', data = record)                
                    

# api endpoint
@admins.route('/view_authorized_columns', methods=['GET', 'POST'])
@roles.admin_token_required
def view_authorized_columns():
    """
    View Column Filter for a user
     
    ---
    tags:
      - Users - Column filtering API
    security:
        - Bearer: []
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: User Id to reset its password
    responses:
      200:
        description: authorized columns view
      400:
        description: authorized columns not view
      403:
        description: Something went wrong
    """
    if not (request.args.get("email")):
            return jsonify({"error": "Incorrect Params"}), 400
    email = request.args.get("email")
    setup_session(request.headers['Authorization'].split()[-1])
    json_obj, status_code = api_util.get_column_filter_for_user_from_api(email)
    return jsonify(json_obj), status_code
    
# application endpoint
@admins.route('/delete_column_filter_ui', methods=['GET', 'POST'])
@roles.admin_token_required
def delete_column_filter_ui():
    """
    Delete filters of columns auth
    ---
    tags:
      - Users - Delete Filter
    security:
        - Bearer: []
    parameters:
      - name: filter_id
        in: query
        type: string
        required: true
        description: Filter ID to disable 
    responses:
      200:
        description: delete filter
      400:
        description: unable to delete filter
      403:
        description: something went wrong
    """

    filter_id = request.args.get('filter_id')
    if not filter_id:
        record = db_obj.get_all_users()
        return render_template('auths/view_user.html', data=record)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    
    if rest_api_condition:
        if not (request.args.get("filter_id")):
            return jsonify({"error": "Incorrect Params"}), 400
        setup_session(request.headers['Authorization'].split()[-1])
        json_obj, status_code = api_util.remove_column_auth_filter(filter_id)
        return jsonify(json_obj), status_code
    else:
        
        user_id = db_obj.get_userid_from_filter_auth_id(filter_id)
        json_obj, status_code = api_util.remove_column_auth_filter(filter_id)
        record = db_obj.get_user_authorized_columns(user_id)
        if status_code==200:
          return render_template('admins/view_filtered_columns.html', flash_message=True, message_toast = "Filter Removed", message_flag = "success", data = record),200                
        return render_template('admins/view_filtered_columns.html', flash_message=True, message_toast = "Unable to Remove the Filter", message_flag = "error", data = record),400

@admins.route('/add_filter', methods=['GET','POST'])
@roles.admin_token_required
def add_filter():
    """
    handles column Filtering
    ---
    tags:
        - Data - Data Filtering
    security:
        - Bearer: []
    parameters:
      - name: user
        in: query
        type: string
        required: true
        description: User's Email
    
      - name: control_table
        in: query
        type: string
        required: true
        description: Control Table Name

      - name: control_area
        in: query
        type: string
        required: true
        description: Control Area

      - name: state
        in: query
        type: string
        required: true
        description: State

      - name: load_zone
        in: query
        type: string
        required: true
        description: Load Zone


      - name: capacity_zone
        in: query
        type:  string
        required: true
        description: Capacity Zone

      - name: utility
        in: query
        type: string
        required: true
        description: Utility

      - name: strip
        in: query
        type: string
        required: true
        description: Strip

      - name: cost_group
        in: query
        type: string
        required: true
        description: Cost Group


      - name: cost_component
        in: query
        type:  string
        required: true
        description: Cost Component

      - name: sub_cost_component
        in: query
        type: string
        required: true
        description: Sub Cost Component

      - name: start
        in: query
        format: date
        type:  string
        required: true
        description: Start Range Date

      - name: end
        in: query
        format: date
        type: string
        required: true
        description: End Range Date


    responses:
      200:
        description: add Filters successfully
      400:
        description: Incorrect parameters provided
      403:
        description: Unable to add data filter

    """

    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
        setup_session(request.headers['Authorization'].split()[-1])
        response, status = api_util.add_filter_api()
        return response, status
    else:
        if request.method == 'POST':
            response, status_code = api_util.add_filter_ui()
            if status_code == 200:
              return render_template('admins/add_filter.html', flash_message=True, message_toast = response['message_toast'], message_flag = "success")
            return render_template('admins/add_filter.html', flash_message=True, message_toast = response['message_toast'], message_flag = "error")
        else:
            return render_template('admins/add_filter.html')


@admins.route('/get_users', methods=['GET', 'POST'])
@roles.admin_token_required
def get_users():

    """
    makes the current drop down dynamic
    """
    users = db_obj.get_all_users_for_dropdown()

    return jsonify(users)

@admins.route('/get_control_area', methods=['GET', 'POST'])
@roles.admin_token_required
def get_control_area():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_areas = db_obj.get_control_area_for_dropdown(table)
      return jsonify(control_areas)
    except:
        return list()
    
@admins.route('/get_state', methods=['GET', 'POST'])
@roles.admin_token_required
def get_state():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_area = request.json['control_area']
      states = db_obj.get_state_for_dropdown(table, control_area)
      return jsonify(states)
    except:
        return list()
    
@admins.route('/get_loadzone', methods=['GET', 'POST'])
@roles.admin_token_required
def get_loadzone():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_area = request.json['control_area']
      state = request.json['state']
      lzones = db_obj.get_load_zone_for_dropdown(table, control_area, state)
      return jsonify(lzones)
    except:
        return list()


@admins.route('/get_capacityzone', methods=['GET', 'POST'])
@roles.admin_token_required
def get_capacityzone():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_area = request.json['control_area']
      loadzone = request.json['load_zone']
      state = request.json['state']
      czones = db_obj.get_capacity_zone_for_dropdown(table, control_area, state, loadzone)
      return jsonify(czones)
    except:
        return list()

@admins.route('/get_utility', methods=['GET', 'POST'])
@roles.admin_token_required
def get_utility():

    """
    makes the current drop down dynamic
    """
    try:
        
      table = request.json['control_table']
      control_area = request.json['control_area']
      loadzone = request.json['load_zone']
      capacityzone = request.json['capacity_zone']
      state = request.json['state']
      utilities = db_obj.get_utility_for_dropdown(table, control_area, state, loadzone, capacityzone)
      return jsonify(utilities)
    except:
        return list()


@admins.route('/get_blocktype', methods=['GET', 'POST'])
@roles.admin_token_required
def get_blocktype():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_area = request.json['control_area']
      loadzone = request.json['load_zone']
      capacityzone = request.json['capacity_zone']
      utility = request.json['utility']
      state = request.json['state']
      blocktypes = db_obj.get_block_type_for_dropdown(table, control_area, state, loadzone, capacityzone, utility)
      return jsonify(blocktypes)
    except:
        return list()


@admins.route('/get_costgroup', methods=['GET', 'POST'])
@roles.admin_token_required
def get_costgroup():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_area = request.json['control_area']
      loadzone = request.json['load_zone']
      capacityzone = request.json['capacity_zone']
      utility = request.json['utility']
      blocktype =  request.json['strip']
      state = request.json['state']
      costgroups = db_obj.get_cost_group_for_dropdown(table, control_area, state, loadzone, capacityzone, utility, blocktype)
      return jsonify(costgroups)
    except:
        return list()

@admins.route('/get_costcomponent', methods=['GET', 'POST'])
@roles.admin_token_required
def get_costcomponent():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_area = request.json['control_area']
      loadzone = request.json['load_zone']
      capacityzone = request.json['capacity_zone']
      utility = request.json['utility']
      blocktype =  request.json['strip']
      costgroup = request.json['cost_group']
      state = request.json['state']
      costcomponents = db_obj.get_cost_components_for_dropdown(table, control_area, state, loadzone, capacityzone, utility, blocktype, costgroup)
      return jsonify(costcomponents)
    except:
        return list()

@admins.route('/get_subcostcomponent', methods=['GET', 'POST'])
@roles.admin_token_required
def get_subcostcomponent():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']
      control_area = request.json['control_area']
      loadzone = request.json['load_zone']
      capacityzone = request.json['capacity_zone']
      utility = request.json['utility']
      blocktype =  request.json['strip']
      costgroup = request.json['cost_group']
      costcomponent = request.json['cost_component']
      state = request.json['state']
      subcostcomponents = db_obj.get_sub_cost_components_for_dropdown(table, control_area, state, loadzone, capacityzone, utility, blocktype, costgroup, costcomponent)
      return jsonify(subcostcomponents)
    except:
        return list()
