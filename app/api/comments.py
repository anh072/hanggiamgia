from flask import request, jsonify, url_for, current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from datetime import datetime

from . import api
from ..models import Post, Comment
from .. import db
from .errors import bad_request, forbidden, internal_error
from .validations import CreateCommentInput


@api.route("/posts/<int:id>/comments")
def get_post_comments(id):
    current_app.logger.info(f"Retrieving comments for post {id}")
    try:
        post = Post.query.get_or_404(id)
        start_comment = request.args.get('start_comment', None, type=int)
        offset = request.args.get('offset', None, type=int)
        if not offset:
            offset = current_app.config["INITIAL_COMMENTS_PER_POST"]
        if not start_comment:
            comments = Comment.query.filter_by(post_id=id) \
                .order_by(Comment.created_time.desc()) \
                .limit(offset) \
                .all()
        else:
            comments = Comment.query.filter(and_(Comment.post_id==id, Comment.id <= start_comment)) \
                .order_by(Comment.created_time.desc()) \
                .limit(offset) \
                .all()
        count = Comment.query.filter_by(post_id=id).count()
        return jsonify({
            'comments': [comment.to_json() for comment in comments],
            'count': count
        })
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")


@api.route("/posts/<int:id>/comments", methods=["POST"])
def new_post_comments(id):
    current_app.logger.info(f"Adding a new comment for post {id}")
    validator = CreateCommentInput(request)
    if not validator.validate():
        return bad_request(validator.errors)
    
    try:
        post = Post.query.get_or_404(id)
        comment = Comment.from_json(request.json)
        author = request.headers.get("username")
        if not author:
            return bad_request("Missing username header")
        comment.author = author
        comment.post = post
        db.session.add(comment)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
    return jsonify(comment.to_json()), 201


@api.route("/posts/<int:post_id>/comments/<int:comment_id>", methods=["PUT"])
def edit_comment(post_id, comment_id):
    current_app.logger.info(f"Editing comment {comment_id} for post {post_id}")
    try:
        comment = Comment.query.get_or_404(comment_id)
        editor = request.headers.get("username")
        if editor != comment.author:
            return forbidden(f"{editor} is not the comment's owner")
        if comment.post_id != post_id:
            return forbidden(f"The comment is not for {post_id}")
        comment.text = request.json.get("text", comment.text)
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_json())
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")


@api.route("/posts/<int:post_id>/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(post_id, comment_id):
    current_app.logger.info(f"Deleteing comment {comment_id} from post {post_id}")
    try:
        comment = Comment.query.get_or_404(comment_id)
        editor = request.headers.get("username")
        if editor != comment.author:
            return forbidden(f"{editor} is not the comment's owner")
        if comment.post_id != post_id:
            return forbidden(f"The comment is not for {post_id}")
        db.session.delete(comment)
        db.session.commit()
        return "Deleted", 200
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")