import io
import uuid

import boto3
from botocore.exceptions import ClientError
from flask import current_app
from PIL import Image


def mask_email(email):
    address, domain = email.split("@")
    mask_length = 1 if len(address) <= 6 else 3
    new_email = address[:mask_length] + "****" + address[len(address)-mask_length:] + "@" + domain
    return new_email


def upload_image_to_s3(bucket, image, username):
    # resize the image
    image = Image.open(io.BytesIO(image.read()))
    image.thumbnail((150, 150))

    # prepare for S3 upload
    buffer = io.BytesIO()
    image.save(buffer, image.format)
    buffer.seek(0)
    image_name = f"{uuid.uuid4().hex}.{image.format.lower()}"

    s3_client = boto3.client("s3")
    aws_region = current_app.config["AWS_REGION"]

    s3_client.put_object(
        ACL="public-read",
        Body=buffer,
        Bucket=bucket,
        Key=image_name,
        Metadata={"username": username},
        ContentType=f"image/{image.format.lower()}"
    )

    image_url = f"https://{bucket}.s3-{aws_region}.amazonaws.com/{image_name}"
    return image_url