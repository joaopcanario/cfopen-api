from flask import Blueprint, redirect, url_for, jsonify


core_bp = Blueprint("core_bp", __name__)


@core_bp.route('/', methods=['GET'])
def root():
    try:
        return redirect(url_for('flasgger.apidocs')), 302
    except Exception:
        return jsonify("API Documentation isn't loaded!"), 200
