import json

import boto3
from flask import current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from . import api
from ..models import Reason, Report
from .errors import internal_error
from .validations import ReportInput
from .. import db
from .errors import bad_request, internal_error


sns_client = boto3.client("sns")


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
    current_app.logger.info("Submitting a report")
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
        sns_client.publish(
            TopicArn=current_app.config["REPORT_TOPIC"],
            Message=json.dumps(request.json),
            Subject="GIARE-REPORT"
        )
        db.session.commit()
        return jsonify(report.to_json()), 201
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
