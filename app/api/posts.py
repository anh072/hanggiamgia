from flask import jsonify, request, current_app, url_for
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from . import api
from ..models import Post, Category
from .. import db
from .errors import bad_request, forbidden, not_found, internal_error
from .validations import CreatePostInput


@api.route("/posts", methods=["GET"])
def get_posts():
    current_app.logger.info("Retrieving posts")
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.created_time.desc()) \
        .paginate(
            page,
            per_page=current_app.config["POSTS_PER_PAGE"],
            error_out=False
        )
    posts = pagination.items
    return jsonify({
        "posts": [post.to_json() for post in posts],
        "limit": current_app.config["POSTS_PER_PAGE"],
        "count": pagination.total
    })


@api.route("/posts/<int:id>", methods=["GET"])
def get_post(id):
    current_app.logger.info(f"Retrieving post by {id}")
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route("/posts", methods=["POST"])
def create_post():
    current_app.logger.info("Creating a new post")
    validator = CreatePostInput(request)
    if not validator.validate():
        return bad_request(validator.errors)

    post = Post.from_json(request.json)
    author = request.headers.get("username")
    if not author:
        return bad_request("Missing username header")
    post.author = author
    try:
        db.session.add(post)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}


@api.route("/posts/<int:id>", methods=["PUT"])
def edit_post(id):
    current_app.logger.info(f"Editing post {id}")
    editor = request.headers.get("username")
    try:
        post = Post.query.get_or_404(id)
        if editor != post.author:
            return forbidden(f"{editor} is not the post's owner")
        post.update_from_json(request.json)
        db.session.add(post)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(r)
        db.session.rollback()
        return internal_error("Encounter unexpected error")
    return jsonify(post.to_json())


@api.route("/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    current_app.logger.info(f"Deleting post {id}")
    try:
        post = Post.query.get_or_404(id)
        editor = request.headers.get("username")
        if editor != post.author:
            return forbidden(f"{editor} is not the post's owner")
        db.session.delete(post)
        db.session.commit()
        return "Deleted", 200
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return internal_error("Encounter unexpected error")


@api.route("/posts/search", methods=["GET"])
def search_posts():
    current_app.logger.info("Searching for post")
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", None, type=str)
    search_key = request.args.get("term", None, type=str)
    if not category or category == "All":
        if search_key:
            pagination = Post.query.filter(Post.title.ilike(f"%{search_key}%")) \
                .order_by(Post.created_time.desc()) \
                .paginate(                
                    page,
                    per_page=current_app.config["POSTS_PER_PAGE"],
                    error_out=False)
        else:
            pagination = Post.query.order_by(Post.created_time.desc()) \
                .paginate(                
                    page,
                    per_page=current_app.config["POSTS_PER_PAGE"],
                    error_out=False)
    else:
        if search_key:
            pagination = Post.query.join(Category) \
                .filter(
                    and_(
                        Post.title.ilike(f"%{search_key}%"), 
                        Category.name == category)) \
                .order_by(Post.created_time.desc()) \
                .paginate(
                    page,
                    per_page=current_app.config["POSTS_PER_PAGE"],
                    error_out=False)
        else:
            pagination = Post.query.join(Category) \
                .filter(Category.name == category) \
                .order_by(Post.created_time.desc()) \
                .paginate(
                    page,
                    per_page=current_app.config["POSTS_PER_PAGE"],
                    error_out=False)     
    posts = pagination.items
    return jsonify({
        "posts": [post.to_json() for post in posts],
        "limit": current_app.config["POSTS_PER_PAGE"],
        "count": pagination.total
    })


@api.route("/posts/max-id", methods=["GET"])
def get_post_max_id():
    current_app.logger.info(f"Retrieving maximum post id")
    post = Post.query.order_by(Post.id.desc()).limit(1).first()
    print(post)
    return jsonify({
        "id": post.id
    })