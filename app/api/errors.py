from flask import current_app, jsonify

from . import api


def bad_request(message):
    current_app.logger.info(f"Bad request: {message}")
    response = jsonify({"error": "bad request", "message": message})
    response.status_code = 400
    return response


def forbidden(message):
    current_app.logger.info(f"Forbidden: {message}")
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response