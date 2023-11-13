import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .util import Util
from .graphview_model import GraphView_Util
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.keys import secret_key, secret_salt
from utils.blocked_tokens import revoked_jwt


graph_view = Blueprint('graph_view', __name__,
                    template_folder="../templates/",
                    static_folder='static')


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
@roles.admin_token_required
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
@roles.admin_token_required
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
@roles.admin_token_required
def load_zones():
    """
    returns the load zones
    """
    table = request.args.get("control_table")
    strip = '5x16'
    load_zones = db_obj.get_load_zones(table, strip)
    return jsonify(load_zones)

@graph_view.route('/intraday_timestamps', methods=['GET'])
@roles.admin_token_required
def intraday_timestamps():
    """
    returns the intraday timestamps
    """
    table = request.args.get("control_table")
    operating_day = request.args.get("operating_day") 
    strip = '5x16'
    timestamps = db_obj.get_intraday_timestamps(table,operating_day, strip)
    return jsonify(timestamps)
  


@graph_view.route('/graph/<control_table>/<location>/<start>/<end>/<operating_day>/<history>/<cob>/<operating_day_timestamp>', methods=['GET', 'POST'])
@roles.admin_token_required
def graphs(control_table, location, start, end,operating_day,history,cob,operating_day_timestamp):
  """
  generates the graph
  """
  rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
  graph = api_util.generate_line_chart (eval(control_table), eval(location), eval(start), eval(end),eval(operating_day),eval(history),eval(cob),eval(operating_day_timestamp))
  if rest_api_condition:
    return graph
  else:
    return render_template('graph_view/graph.html',graphJSON=graph)

@graph_view.route('/save_graph', methods=['GET', 'POST'])
@roles.admin_token_required
def save_graph():
  """
  saves the graph 
  """
  token = request.json['token']
  control_table = request.json.get("control_table")
  location = request.json.get("loadZone")
  start_date = request.json.get("start")
  end_date = request.json.get("end")
  operating_day = request.json.get("operating_day")
  history = request.json.get("history")
  cob = request.json.get("cob")
  operatin_day_timestamps = request.json.get("operatin_day_timestamps")

  email = api_util.get_email(token)
  flag = db_obj.save_graph_url(email, control_table, location, start_date, end_date,operating_day,history,cob,operatin_day_timestamps,"self")
  data = db_obj.get_user_graphs(email)
  rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
  if rest_api_condition:
    if flag:
      return jsonify("graph saved successfully"), 200
    return jsonify("unable to save graph"), 200
  else:
    if flag:
      #  success response
      return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "graph saved successfully", message_flag = "success")
    else:
      #  error response
      return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "unable to save graph", message_flag = "error")
  

@graph_view.route('/remove_graph', methods=['GET', 'POST'])
@roles.admin_token_required
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
      return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "graph view removed successfully", message_flag = "success")
    else:
      #  error response
      return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "unable to remove graph", message_flag = "error")
  
@graph_view.route('/available_graphs', methods=['GET', 'POST'])
@roles.admin_token_required
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
@roles.admin_token_required
def share_graphs():
  """
  share graphs
  """
  graph_id = request.args.get("graph_id")
  emails = db_obj.get_emails()
  if request.method=="POST":
    email = request.form.get("email")
    flag = db_obj.share_graph(email, graph_id)

    user_email = api_util.get_email(session["jwt_token"])
    data = db_obj.get_user_graphs(user_email)
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
      if flag:
        return jsonify("graph shared successfully"), 200
      return jsonify("unable to share graph"), 200
    else:
      if flag:
        return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "graph shared successfully", message_flag = "success")
      else:
        return render_template("graph_view/graphview_data.html", data=data, flash_message=True, message_toast = "unable to share the graph", message_flag = "error")  
  return render_template("graph_view/share_graph.html", emails=emails)

@graph_view.route('/view_graphs', methods=['GET', 'POST'])
@roles.admin_token_required
def view_graphs():
  """
  generates the graph
  """
  graph_id = request.args.get("graph_id")
  control_table_data, location, cob_data, history_data, startdate_data, enddate_data, operating_day_data, operating_day_timestamps_data = api_util.get_graphs(graph_id)
  # control_table, location, start, end,operating_day,history,cob,operating_day_timestamp 
  rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
  graph = api_util.generate_line_chart (control_table_data, location, startdate_data, enddate_data, operating_day_data ,history_data, cob_data, operating_day_timestamps_data)
  if rest_api_condition:
    return graph
  else:
    return render_template('graph_view/graph.html',graphJSON=graph)


  

  
   


    
