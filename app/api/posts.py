from flask import jsonify, request, current_app, url_for
from sqlalchemy import and_

from . import api
from ..models import Post, Category
from .. import db
from .errors import bad_request, forbidden
from .validations import CreatePostInput, SearchPostInput, UpdatePostVoteInput


@api.route("/posts", methods=["GET"])
def get_posts():
    current_app.logger.info("Retrieving posts")
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", None, type=str)
    if not category:
        pagination = Post.query.order_by(Post.created_time.desc()) \
            .paginate(
                page,
                per_page=current_app.config["POSTS_PER_PAGE"],
                error_out=False
            )
    else:
        pagination = Post.query.join(Category) \
            .filter(Category.name == category) \
            .order_by(Post.created_time.desc()) \
            .paginate(
                page,
                per_page=current_app.config["POSTS_PER_PAGE"],
                error_out=False
            )
    posts = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for("api.get_posts", page=page-1)
    if pagination.has_next:
        next = url_for("api.get_posts", page=page+1)
    return jsonify({
        "posts": [post.to_json() for post in posts],
        "prev": prev,
        "next": next,
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
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}


@api.route("/posts/<int:id>", methods=["PUT"])
def edit_post(id):
    current_app.logger.info(f"Editing post {id}")
    post = Post.query.get_or_404(id)

    editor = request.headers.get("username")
    if editor != post.author:
        return forbidden(f"{editor} is not the post's owner")
    post.text = request.json.get("text", post.text)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route("/posts/<int:id>/votes", methods=["PUT"])
def update_post_votes(id):
    current_app.logger.info(f"Updating vote count for post {id}")
    post = Post.query.get_or_404(id)

    validator = UpdatePostVoteInput(request)
    if not validator.validate():
        return bad_request(validator.errors)
    
    if action == "increment":
        post.votes += 1
    else:
        if post.votes > 0:
            post.votes -= 1
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route("/posts/search", methods=["POST"])
def search_posts():
    current_app.logger.info("Searching for post")
    validator = SearchPostInput(request)
    if not validator.validate():
        return bad_request(validator.errors)

    page = request.args.get("page", 1, type=int)
    category = request.json.get("category")
    search_key = request.json.get("key")
    if category == "All":
        pagination = Post.query.filter(Post.title.ilike(f"%{search_key}%")) \
            .order_by(Post.created_time.desc()) \
            .paginate(                
                page,
                per_page=current_app.config["POSTS_PER_PAGE"],
                error_out=False)
    else:
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
    posts = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for("api.search_posts", page=page-1)
    if pagination.has_next:
        next = url_for("api.search_posts", page=page+1)
    return jsonify({
        "posts": [post.to_json() for post in posts],
        "prev": prev,
        "next": next,
        "count": pagination.total
    })