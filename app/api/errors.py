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


def not_found(message):
    current_app.logger.info(f"Not Found: {message}")
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response


def internal_error(message):
    current_app.logger.error(f"Internal error: {message}")
    response = jsonify({'error': 'internal server error', 'message': message})
    response.status_code = 404
    return response