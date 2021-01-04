from flask import request, jsonify, url_for, current_app
from sqlalchemy.exc import SQLAlchemyError

from . import api
from ..models import Post, Comment
from .. import db
from .errors import bad_request, forbidden, internal_error
from .validations import CreateCommentInput


@api.route("/posts/<int:id>/comments")
def get_post_comments(id):
    current_app.logger.info(f"Retrieving comments for post {id}")
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(
        Comment.created_time.asc()).paginate(
            page, 
            per_page=current_app.config["COMMENTS_PER_PAGE"],
            error_out=False
        )
    comments = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1)
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page+1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


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
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
    return jsonify(comment.to_json())