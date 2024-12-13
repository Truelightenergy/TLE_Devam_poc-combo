import os
import logging
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from blueprints.auths.view import auths
from blueprints.admins.view import admins
from blueprints.extractors.view import extractors
from blueprints.ingestors.view import ingestors
from blueprints.graph_view.view import graph_view
from blueprints.headrooms.view import headrooms
from blueprints.pricingdesk.views import price
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from utils.configs import read_config

config = read_config()



logging.basicConfig(level=logging.INFO)


# logs saving
logger = logging.getLogger()
# fileHandler = RotatingFileHandler("logs.log", maxBytes=1)
# logger.addHandler(fileHandler)

# logs console
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

LOG_FOLDER = config['logging_folder']
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logHandler = TimedRotatingFileHandler(f"{LOG_FOLDER}{config['time_log']}", when='D', interval=1)
logger.addHandler(logHandler)

revoked_jwt = RevokedTokens()
roles = RolesDecorator(revoked_jwt)




def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    

    app.config['SESSION_TYPE'] = config['app_session_type']
    app.secret_key = config['app_secret_key']
    
    app.register_blueprint(auths)
    app.register_blueprint(admins)
    app.register_blueprint(ingestors)
    app.register_blueprint(extractors)
    app.register_blueprint(graph_view)
    app.register_blueprint(headrooms)
    app.register_blueprint(price)

    return app
template = {
    "securityDefinitions": {
        "Bearer":
            {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                 'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
            }
    }
}

logging.info(f"Starting {__name__}")
app = create_app()
swagger = Swagger(app, template=template)

if __name__ == "__main__":
    app.run(port=5555)