import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .headroom_util import Util
from .headroom_model import HeadroomModel
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.configs import read_config
from utils.blocked_tokens import revoked_jwt

config = read_config()
headrooms = Blueprint(config['headrooms_path'], __name__,
                    template_folder=config['template_path'],
                    static_folder=config['static_path'])

secret_key = config['secret_key']
secret_salt = config['secret_salt']
db_obj = HeadroomModel(secret_key, secret_salt)
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

@headrooms.route('/generate_headroom_heatmap', methods=['GET', 'POST'])
@roles.readonly_token_required
def generate_headroom_heatmap():

    """
    Heatmaps generation
    ---
    tags:
      - Headroom Heatmap
    security:
        - Bearer: []
    responses:
      200:
        description: heatmap generation
      400:
        description: unable to graph generation
      403:
        description: something went wrong
    """
    rest_api_condition =  not ('text/html' in request.headers.get('Accept', ''))

    graph = api_util.get_headroom_heatmap()
    if rest_api_condition:
        return graph
    else:
        return render_template('headrooms/generate_headroom_heatmap.html',data=graph)


    
