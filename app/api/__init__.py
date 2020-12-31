from flask import Blueprint, current_app
from flask_sqlalchemy import get_debug_queries

api = Blueprint("api", __name__)

@api.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["SLOW_DB_QUERY_TIME"]:
            current_app.logger.warning(f"Slow query: {query.statement}, Parameters: {query.parameters}, Duration: {query.duration}, Context: {query.context}")
    return response

from . import users, posts, comments, errors, validations