from flask import current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError

from . import api
from ..models import Category
from .errors import internal_error


@api.route("/categories", methods=["GET"])
def get_categories():
    current_app.logger.info("Retrieving all categories")
    try:
      categories = Category.query(Category.name).all()
    except SQLAlchemyError as e:
      current_app.logger.rror(e)
      return internal_error("Encounter unexpected error")
    return jsonify({"categories": categories})