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
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
    if rest_api_condition:
      data_type = request.args.get("data_type")
      control_table = request.args.get("control_table")
      location = request.args.get("sub_cost_component")
      start_date = request.args.get("start")
      end_date = request.args.get("end")
      return redirect(url_for('.graphs', control_table=control_table, location=location, start=start_date, end=end_date))
    
    else:
        
      if request.method=="POST":
        data_type = request.form.get("data_type")
        control_table = request.form.get("control_table")
        location = request.form.get("sub_cost_component")
        start_date = request.form.get("start")
        end_date = request.form.get("end")

        return redirect(url_for('.graphs', control_table=control_table, location=location, start=start_date, end=end_date))    
      return render_template('graph_view/generate_graph.html')



@graph_view.route('/graph/<control_table>/<location>/<start>/<end>', methods=['GET', 'POST'])
@roles.admin_token_required
def graphs(control_table, location, start, end):
  """
  generates the graph
  """
  rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))
  graph = api_util.generate_line_chart (control_table, location, start, end)
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
  url = request.json['url']
  token = request.json['token']

  email = api_util.get_email(token)
  flag = db_obj.save_graph_url(email, url, "self")
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
  url = request.args.get("graph_url")
  emails = db_obj.get_emails()
  if request.method=="POST":
    email = request.form.get("email")
    flag = db_obj.save_graph_url(email, url, "shared")

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
  return render_template("graph_view/share_graph.html", data=url, emails=emails)


  

  
   


    
