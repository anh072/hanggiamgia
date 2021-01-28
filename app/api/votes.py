from flask import jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError

from . import api
from ..models import Post, Vote, VoteTypeEnum
from .. import db
from .errors import bad_request, forbidden, not_found, internal_error
from .validations import UpdatePostVoteInput


@api.route("/posts/<int:id>/votes", methods=["PUT"])
def update_post_votes(id):
    current_app.logger.info(f"Updating vote count for post {id}")
    username = request.headers.get("username")

    validator = UpdatePostVoteInput(request)
    if not validator.validate():
        return bad_request(validator.errors)
    
    try:
        post = Post.query.with_for_update(of=Post).filter(Post.id == id).first()
        if not post:
            return not_found("Post is not found")
        vote = Vote.query.filter_by(post_id=id, voter=username).first()
        if vote:
            return bad_request(f"User {username} has already voted")

        action = request.json.get("vote_action")
        if action == "increment":
            post.votes += 1
            vote_type = VoteTypeEnum.INCREMENT
        else:
            post.votes -= 1
            vote_type = VoteTypeEnum.DECREMENT

        new_vote = Vote(
            post_id=id,
            voter=username,
            vote_type=vote_type
        )
        db.session.add(post)
        db.session.add(new_vote)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
    return jsonify(post.to_json())


@api.route("/posts/<int:id>/votes", methods=["GET"])
def get_post_votes(id):
    current_app.logger.info(f"Retrieving votes for post {id}")
    post = Post.query.filter(Post.id == id).first()
    if not post:
        return not_found("Post is not found")
    votes = Vote.query.filter_by(post_id=id)
    return jsonify({
        "votes": [v.to_json() for v in votes]
    })


@api.route("/posts/<int:post_id>/votes/<int:vote_id>", methods=["DELETE"])
def revoke_vote(post_id, vote_id):
    current_app.logger.info(f"Revoke vote {vote_id} for post {post_id}")
    user = request.headers.get("username")
    try:
        post = Post.query.with_for_update(of=Post).filter(Post.id == post_id).first()
        if not post:
            return not_found("Post is not found")
        vote = Vote.query.filter_by(post_id=post_id, id=vote_id).first()
        if not vote:
            return not_found("Vote is not found")
        if vote.voter != user:
            return forbidden("Vote does not belong to the user")
        if vote.vote_type.value == "increment":
            post.votes -= 1
        else:
            post.votes += 1
        db.session.add(post)
        db.session.delete(vote)
        db.session.commit()
        return "Deleted"
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
    