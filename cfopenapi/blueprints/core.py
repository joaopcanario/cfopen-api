from flask import Blueprint, redirect, url_for


core_bp = Blueprint("core_bp", __name__)


@core_bp.route('/', methods=['GET'])
def root():
    return redirect(url_for('flasgger.apidocs')), 302