from flask import current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from . import api
from ..models import Reason, Report
from .errors import internal_error
from .validations import ReportInput
from .. import db
from .errors import bad_request, internal_error


@api.route("/reasons", methods=["GET"])
def get_reasons():
    current_app.logger.info("Retrieving all report reasons")
    try:
        reasons = Reason.query.with_entities(Reason.name).all()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return internal_error("Encounter unexpected error")
    return jsonify({"reasons": [r[0] for r in reasons]})


@api.route("/reports", methods=["POST"])
def report():
    validator = ReportInput(request)
    if not validator.validate():
        return bad_request(validator.errors)

    report = Report.from_json(request.json)
    reporter = request.headers.get("username")
    if not reporter:
        return bad_request("Missing username header")
    report.reporter = reporter
    try:
        db.session.add(report)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
    return jsonify(report.to_json()), 201