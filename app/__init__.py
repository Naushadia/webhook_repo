from flask import Flask
import os
from app.webhook.routes import webhook
from flask_cors import CORS


def create_app():

    template_dir = os.path.abspath("templates")
    app = Flask(__name__, template_folder=template_dir)
    CORS(app)

    @app.route("/", methods=["GET"])
    def index():
        return "Welcome to our homepage!"

    app.register_blueprint(webhook)

    return app
