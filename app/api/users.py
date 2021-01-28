import io
import uuid

from flask import jsonify, request, current_app, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import boto3
from botocore.exceptions import ClientError

from . import api
from ..models import Post, Image as ImageModel, Comment
from .errors import bad_request
from .. import db


@api.route("/users/<string:username>/posts", methods=["GET"])
def get_posts_by_username(username):
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.filter_by(author=username) \
        .paginate(
            page, 
            per_page=current_app.config["POSTS_PER_PAGE"],
            error_out=False)
    posts = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for("api.get_posts_by_username", page=page-1)
    if pagination.has_next:
        next = url_for("api.get_posts_by_username", page=page+1)
    return jsonify({
        "posts": [post.to_json() for post in posts],
        "prev": prev,
        "next": next,
        "count": pagination.total
    })


@api.route("/users/<username>/images/upload", methods=["POST"])
def image_upload(username):
    current_app.logger.info(f"Uploading image for user {username}")
    if not request.files or "image" not in request.files:
        return bad_request("No image was uploaded")
    image = request.files["image"]
    if image.filename == "":
        return bad_request("No file was selected")
    if image.filename.rsplit('.', 1)[1].lower() not in current_app.config["UPLOAD_EXTENSIONS"]:
        return bad_request(f"Only accept file extensions: {current_app.config['UPLOAD_EXTENSIONS']}")
    
    # resize the image
    image = Image.open(io.BytesIO(image.read()))
    image.thumbnail((150, 150))

    # prepare for S3 upload
    buffer = io.BytesIO()
    image.save(buffer, image.format)
    buffer.seek(0)
    image_name = f"{uuid.uuid4().hex}.{image.format.lower()}"

    s3_client = boto3.client("s3")
    bucket = current_app.config["S3_IMAGE_BUCKET"]
    aws_region = current_app.config["AWS_REGION"]

    try:
        res = s3_client.put_object(
            ACL="public-read",
            Body=buffer,
            Bucket=bucket,
            Key=image_name,
            Metadata={"username": username},
            ContentType=f"image/{image.format.lower()}"
        )
    except ClientError as e:
        current_app.logger.error(e.response["Error"]["Message"])
        return jsonify({"error": f"S3 error: {e.response['Error']['Code']} {e.response['Error']['Message']}"}), 500

    image_url = f"https://{bucket}.s3-{aws_region}.amazonaws.com/{image_name}"

    image_model = ImageModel(author=username, image_url=image_url)
    db.session.add(image_model)
    db.session.commit()
    return jsonify({"image_url": image_url})


@api.route("/users/<string:username>/commented_posts")
def get_commented_post_by_username(username):
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.join(Comment, Post.id == Comment.post_id) \
        .filter(Comment.author == username) \
        .paginate(
            page, 
            per_page=current_app.config["POSTS_PER_PAGE"],
            error_out=False)
    posts = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for("api.get_commented_post_by_username", page=page-1)
    if pagination.has_next:
        next = url_for("api.get_commented_post_by_username", page=page+1)
    return jsonify({
        "posts": [post.to_json() for post in posts],
        "prev": prev,
        "next": next,
        "count": pagination.total
    })