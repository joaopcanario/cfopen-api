from flask import Blueprint, jsonify


core_bp = Blueprint("core_bp", __name__)


@core_bp.route('/', methods=['GET'])
def root():
    return jsonify(response='Runing'), 200