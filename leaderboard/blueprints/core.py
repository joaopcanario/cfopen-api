from flask import Blueprint, jsonify, request
from flask import current_app as app


core_bp = Blueprint("core_bp", __name__)


@core_bp.route('/', methods=['GET'])
def root():
    return jsonify(response='Runing'), 200