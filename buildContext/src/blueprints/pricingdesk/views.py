import os
from flask import Blueprint, render_template, current_app
from flask import request, jsonify, session, Flask, url_for, redirect
from .pricing_model import PricingDesk
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from utils.configs import read_config
from utils.blocked_tokens import revoked_jwt


config = read_config()
price = Blueprint(config['price_desk'], __name__,
                    template_folder=config['template_path'],
                    static_folder=config['static_path'])


secret_key = config['secret_key']
secret_salt = config['secret_salt']
roles = RolesDecorator(revoked_jwt)


@price.route('/pricedesk', methods=['GET','POST'])
@roles.readwrite_token_required
def pricedesk():
    """
    Start
    """
    price_desk = PricingDesk()
    response = price_desk.calculate_price()
    return response