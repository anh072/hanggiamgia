from flask import jsonify, request, current_app, url_for
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import requests

from . import api
from ..models import Post, Image as ImageModel, Comment
from .errors import bad_request, not_found, internal_error
from .. import db
from .auth import get_access_token
from .utils import mask_email, upload_image_to_s3


@api.route("/users/<string:username>/posts", methods=["GET"])
def get_posts_by_username(username):
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.filter_by(author=username) \
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


@api.route("/users/<string:username>/images/upload", methods=["POST"])
def image_upload(username):
    current_app.logger.info(f"Uploading image for user {username}")
    if not request.files or "image" not in request.files:
        return bad_request("No image was uploaded")
    image = request.files["image"]
    if image.filename == "":
        return bad_request("No file was selected")
    if image.filename.rsplit('.', 1)[1].lower() not in current_app.config["UPLOAD_EXTENSIONS"]:
        return bad_request(f"Only accept file extensions: {current_app.config['UPLOAD_EXTENSIONS']}")
    
    bucket = current_app.config["S3_POST_IMAGE_BUCKET"]

    try:
        image_url = upload_image_to_s3(bucket, image, username)
    except ClientError as e:
        current_app.logger.error(e.response["Error"]["Message"])
        return internal_error("Unexpected error")

    image_model = ImageModel(author=username, image_url=image_url)
    db.session.add(image_model)
    db.session.commit()
    return jsonify({"image_url": image_url})


@api.route("/users/<string:username>/commented_posts", methods=["GET"])
def get_commented_post_by_username(username):
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.join(Comment, Post.id == Comment.post_id) \
        .filter(Comment.author == username) \
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


@api.route("/users/<string:username>", methods=["GET"])
def get_user_by_username(username):
    try:
        access_token = get_access_token()
        res = requests.get(
            f"https://{current_app.config['AUTH0_API_DOMAIN']}/api/v2/users?q=username%3A%22{username}%22&search_engine=v3",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        res.raise_for_status()
        data = res.json()
        if not len(data):
            return not_found("User is not found")
        user = data[0]
        return jsonify({
            "user": {
                "created_time": user["created_at"],
                "username": user["username"],
                "email": mask_email(user["email"]),
                "picture": user["picture"]
            }
        })
    except requests.RequestException as e:
        current_app.logger.error(e)
        return internal_error("Unexpecter error")


@api.route("/users/profile-image", methods=["POST"])
def profile_image_upload():
    user_id = request.headers.get("userId")
    username = request.headers.get("username")

    current_app.logger.info(f"Uploading profile picture for user {username}")
    if not request.files or "image" not in request.files:
        return bad_request("No image was uploaded")
    image = request.files["image"]
    if image.filename == "":
        return bad_request("No file was selected")
    if image.filename.rsplit('.', 1)[1].lower() not in current_app.config["UPLOAD_EXTENSIONS"]:
        return bad_request(f"Only accept file extensions: {current_app.config['UPLOAD_EXTENSIONS']}")
    
    try:
        bucket = current_app.config["S3_PROFILE_IMAGE_BUCKET"]
        image_url = upload_image_to_s3(bucket, image, username)
    except ClientError as e:
        current_app.logger.error(e.response["Error"]["Message"])
        return internal_error("Unexpected error")
    
    try:
        access_token = get_access_token()
        res = requests.patch(
            f"https://{current_app.config['AUTH0_API_DOMAIN']}/api/v2/users/{user_id}",
            json={
                "user_metadata": {
                    "picture": image_url
                }
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        if res.status_code == 404:
            return not_found("User is not found")
        res.raise_for_status()
        return jsonify({
            "message": "Profile image is uploaded successfully"
        })
    except requests.RequestException as e:
        current_app.logger.error(e)
        return internal_error("Unexpecter error")