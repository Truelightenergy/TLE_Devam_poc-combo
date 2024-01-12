import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .util import Util
from .graphview_model import GraphView_Util
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.configs import read_config
from utils.blocked_tokens import revoked_jwt

config = read_config()

graph_view = Blueprint(config['graph_view_path'], __name__,
                    template_folder=config['template_path'],
                    static_folder=config['static_path'])

secret_key = config['secret_key']
secret_salt = config['secret_salt']
db_obj = GraphView_Util(secret_key, secret_salt)
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

@graph_view.route('/get_locations', methods=['GET', 'POST'])
@roles.readonly_token_required
def get_locations():

    """
    makes the current drop down dynamic
    """
    try:
      table = request.json['control_table']

      subcostcomponents = db_obj.get_locations_data(table)
      return jsonify(subcostcomponents)
    except:
        return list()
    
    
@graph_view.route('/generate_garph_view', methods=['GET', 'POST'])
@roles.readonly_token_required
def generate_garph_view():

    """
    Graph view generation
    ---
    tags:
      - Graph View - graph generation
    security:
        - Bearer: []
    parameters:
      - name: data_type
        in: query
        type: string
        required: true
        description: ptc or headroom

      - name: control_table
        in: query
        type: string
        required: true
        description: ercot_energy etc

      - name: sub_cost_component
        in: query
        type: string
        required: true
        description: WEST ZONE

      - name: start
        in: query
        type: string
        required: true
        description: date 2022-01-01

      - name: end
        in: query
        type: string
        required: true
        description: date 2022-01-01

    responses:
      200:
        description: graph generation
      400:
        description: unable to graph generation
      403:
        description: something went wrong
    """
    if request.method=="POST":
      data_type = request.json.get("data_type")
      control_table = request.json.get("control_table")
      location = request.json.get("loadZone")
      start_date = request.json.get("start")
      end_date = request.json.get("end")
      operating_day = request.json.get("operating_day")
      history = request.json.get("history")
      cob = request.json.get("cob")
      operatin_day_timestamps = request.json.get("operatin_day_timestamps")
      return redirect(url_for('.graphs', control_table=control_table, location=location,
                                start=start_date, 
                                end=end_date,
                                operating_day = operating_day,
                                history=history, 
                                cob=cob,
                                operating_day_timestamp=operatin_day_timestamps))    
    else:      
      return render_template('graph_view/generate_graph.html')

@graph_view.route('/load_zones', methods=['GET'])
@roles.readonly_token_required
def load_zones():
    """
    returns the load zones
    """
    table = request.args.get("control_table")
    strip = '5x16'
    load_zones = db_obj.get_load_zones(table, strip)
    return jsonify(load_zones)

@graph_view.route('/intraday_timestamps', methods=['GET'])
@roles.readonly_token_required
def intraday_timestamps():
    """
    returns the intraday timestamps
    """
    table = request.args.get("control_table")
    operating_day = request.args.get("operating_day") 
    strip = '5x16'
    timestamps = db_obj.get_intraday_timestamps(table,operating_day, strip)
    return jsonify(timestamps)
  

@graph_view.route('/graph', defaults={'graph_id': None})
@graph_view.route('/graph/<graph_id>', methods=['GET'])
@roles.readonly_token_required
def graphs(graph_id):
  """
  generates the graph
  """
  if(graph_id is None):
    return render_template('graph_view/graph.html')
  else :
    graph_details = db_obj.get_graph_data(graph_id)
    return render_template('graph_view/graph.html', graph_details=graph_details)
    
  
@graph_view.route('/graphs', methods=[ 'POST'])
@roles.readonly_token_required
def graphsMultiLine():
  """
  Generates the graph based on posted parameters.
  """
  # Ensure the request is JSON and get the payload
  if not request.is_json:
      return jsonify({"msg": "Missing JSON in request"}), 400

  # Extract parameters from the JSON payload
  params_array = request.get_json()

  # Call the generate_line_charts method with the array of parameters
  graph = api_util.generate_line_charts(params_array)

  # Decide the response based on the 'Accept' header in the request
  rest_api_condition = not ('text/html' in request.headers.get('Accept', ''))
  if rest_api_condition:
      return graph  # Return the graph JSON for API consumers
  else:
      return render_template('graph_view/graph.html', graphJSON=graph)  # Render a page for browsers

@graph_view.route('/save_graph', methods=['GET', 'POST'])
@roles.readonly_token_required
def save_graph():
  """
  saves the graph 
  """
  token = request.headers['Authorization']
  
  if not request.is_json:
      return jsonify({"msg": "Missing JSON in request"}), 400

  email = api_util.get_email(token.replace("Bearer ", ""))
  flag = db_obj.save_graph_url(email, request.get_json())
  if flag:
    return jsonify("graph saved successfully"), 200
  return jsonify("unable to save graph"), 200  

@graph_view.route('/update_graph_filters/<graph_id>', methods=['PUT'])
@roles.readonly_token_required
def update_graph_filters(graph_id):
  """
  update graph filters
  """
  
  if not request.is_json:
      return jsonify({"msg": "Missing JSON in request"}), 400

  flag = db_obj.update_graph_filters(graph_id, request.get_json())

  if flag:
    return jsonify("graph saved successfully"), 200
  return jsonify("unable to save graph"), 200  
  
  

@graph_view.route('/remove_graph', methods=['GET', 'POST'])
@roles.readonly_token_required
def remove_graph():
  """
  removes the graph 
  """
  
  rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
  graph_id = request.args.get("graph_id")
  flag = db_obj.remove_graphview(graph_id)

  email = api_util.get_email(session["jwt_token"] )
  data = db_obj.get_user_graphs(email)

  if rest_api_condition:
    if flag:
      return jsonify("graph removed successfully"), 200
    return jsonify("unable to remove graph"), 200
  else:
    if flag:
      #  success response
      return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "Graph removed successfully", message_flag = "success")
    else:
      #  error response
      return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "unable to remove graph", message_flag = "error")
  
@graph_view.route('/available_graphs', methods=['GET', 'POST'])
@roles.readonly_token_required
def available_graphs():
  """
  view graphs
  """
  email = api_util.get_email(session["jwt_token"] )
  data = db_obj.get_user_graphs(email)
  rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
  if rest_api_condition:
    return data
  return render_template("graph_view/graphview_data.html", data=data)


@graph_view.route('/share_graphs', methods=['GET', 'POST'])
@roles.readonly_token_required
def share_graphs():
  """
  share graphs
  """  
  graph_id = request.args.get("graph_id")
  emails = db_obj.get_emails()
  if request.method=="POST":
    email = request.form.get("email")
    graph = db_obj.get_graph_data(graph_id)
    flag = db_obj.save_graph_url(email,eval(graph["filters"]), "shared")

    user_email = api_util.get_email(session["jwt_token"])
    data = db_obj.get_user_graphs(user_email)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
      if flag:
        return jsonify("graph shared successfully"), 200
      return jsonify("unable to share graph"), 200
    else:
      if flag:
        return redirect(url_for('.available_graphs'))
      else:
        return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "unable to share the graph", message_flag = "error")  
  return render_template("graph_view/share_graph.html", data=graph_id, emails=emails)


  

  
   


    
