import os
import logging
from flask import Flask
from flasgger import Swagger
from blueprints.auths.view import auths
from blueprints.admins.view import admins
from blueprints.extractors.view import extractors
from blueprints.ingestors.view import ingestors
from utils.revoke_tokens import RevokedTokens
from utils.roles import RolesDecorator
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler



logging.basicConfig(level=logging.INFO)


# logs saving
logger = logging.getLogger()
# fileHandler = RotatingFileHandler("logs.log", maxBytes=1)
# logger.addHandler(fileHandler)

# logs console
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

LOG_FOLDER = './logs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logHandler = TimedRotatingFileHandler(f"{LOG_FOLDER}/time_log.log", when='D', interval=1)
logger.addHandler(logHandler)

revoked_jwt = RevokedTokens()
roles = RolesDecorator(revoked_jwt)




def create_app():
    app = Flask(__name__)
    

    app.config['SESSION_TYPE'] = 'filesystem'
    app.secret_key = 'super secret key' 
    
    app.register_blueprint(auths)
    app.register_blueprint(admins)
    app.register_blueprint(ingestors)
    app.register_blueprint(extractors)

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