from flask import jsonify

from . import api


def bad_request(message):
    response = jsonify({"error": "bad request", "message": message})
    response.status_code = 400
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response


def internal_error(message):
    response = jsonify({'error': 'internal server error', 'message': message})
    response.status_code = 404
    return response