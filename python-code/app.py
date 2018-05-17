
# -*- coding: utf-8 -*-
import os

from flask import Flask, jsonify, make_response
from flask_cors import CORS

from db import db
from api import api
# import config file
import config
from config import LOG_FILE_DIRECTORY
from config import LOG_FILE
from config import LOG_LEVEL


def create_app(config):
    # init our app
    app = Flask(__name__)
    app.secret_key = 'djfjsdkjXXS7979dfdfd'
    # load config values from the config file
    app.config.from_object(config)

    # init sqlalchemy db instance
    db.init_app(app)
    db.app = app
    # register blueprints
    app.register_blueprint(api)
    configure_logging(app)
    configure_errorhandlers(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    #  configure_cors(app)
    # all set; return app object
    return app


# custom error handlers to return JSON errors with appropiate status codes
def configure_errorhandlers(app):

    @app.errorhandler(500)
    def server_error(err):
        app.logger.error("error code = %s" % "500")
        resp = None
        try:
            app.logger.error("error desc = %s" % err.description)
            resp = make_response(jsonify(error=err.description), 500)
        except Exception:
            try:
                app.logger.error("error mesg = %s" % err.message)
                resp = make_response(jsonify(error=err.message), 500)
            except Exception:
                resp = make_response(jsonify(error=str(err)), 500)
                app.logger.error("error = %s" % str(err))
        return resp

    @app.errorhandler(405)
    def method_not_allowed(err):
        app.logger.error("error code = %s" % "405")
        resp = None
        try:
            app.logger.error("error desc = %s" % err.description)
            resp = make_response(jsonify(error=err.description), 405)
        except Exception:
            try:
                app.logger.error("error mesg = %s" % err.message)
                resp = make_response(jsonify(error=err.message), 405)
            except Exception:
                resp = make_response(jsonify(error=str(err)), 405)
                app.logger.error("error = %s" % str(err))
        return resp

    @app.errorhandler(404)
    def not_found(err):
        app.logger.error("error code = %s" % "404")
        resp = None
        try:
            app.logger.error("error desc = %s" % err.description)
            resp = make_response(jsonify(error=err.description), 404)
        except Exception:
            try:
                app.logger.error("error mesg = %s" % err.message)
                resp = make_response(jsonify(error=err.message), 404)
            except Exception:
                resp = make_response(jsonify(error=str(err)), 404)
                app.logger.error("error = %s" % str(err))
        return resp

    @app.errorhandler(400)
    def bad_request(err):
        app.logger.error("error code = %s" % "400")
        resp = None
        try:
            app.logger.error("error desc = %s" % err.description)
            resp = make_response(jsonify(error=err.description), 400)
        except Exception:
            try:
                app.logger.error("error mesg = %s" % err.message)
                resp = make_response(jsonify(error=err.message), 400)
            except Exception:
                resp = make_response(jsonify(error=str(err)), 400)
                app.logger.error("error = %s" % str(err))
        return resp


def configure_logging(app):
    import logging
    import logging.handlers
    formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(filename)s:'
                                  ' %(funcName)s():%(lineno)d: %(message)s')

    # Also error can be sent out via email. So we can also have a SMTPHandler?
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..',
                           LOG_FILE_DIRECTORY)

    log_file = "%s/%s" % (log_dir, LOG_FILE)
    os.system("sudo touch %s" % log_file)
    os.system("sudo chmod 777 %s" % log_file)
    max_size = 1024 * 1024 * 20  # Max Size for a log file: 20MB
    log_handler = logging.handlers.RotatingFileHandler(log_file,
                                                       maxBytes=max_size,
                                                       backupCount=10)

    log_level = LOG_LEVEL
    
    log_handler.setFormatter(formatter)

    app.logger.addHandler(log_handler)
    app.logger.setLevel(log_level)

if __name__ == "__main__":
    app = create_app(config)
    app.run(debug=True, host='0.0.0.0', threaded=True)
