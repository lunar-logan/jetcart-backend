from marshmallow import ValidationError

from jetcart.service import catalog as service
from flask import request, jsonify, Blueprint, render_template
import logging
import traceback

blueprint = Blueprint('presentation', __name__)


@blueprint.route('/')
def index():
    return render_template('hello.html')


@blueprint.route('/catalogapp')
def catalog_app():
    return render_template('catalog/app.html')


@blueprint.errorhandler(Exception)
def error_handler(error):
    logging.error(msg="Exception handling request", exc_info=True)
    return render_template('error.html', message=str(traceback.format_exc())), getattr(error, 'status_code', 500)
