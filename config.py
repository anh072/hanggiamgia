import os


class Config:
    POSTS_PER_PAGE = 4
    INITIAL_COMMENTS_PER_POST = 2
    SLOW_DB_QUERY_TIME = 0.5
    MAX_CONTENT_LENGTH = 1024*1024
    UPLOAD_EXTENSIONS = ["jpg", "png", "jpeg"]
    AWS_REGION = "ap-southeast-2"
    AUTH0_API_AUDIENCE = "https://dev-d5keivxi.au.auth0.com/api/v2/"
    AUTH0_API_DOMAIN = "dev-d5keivxi.au.auth0.com"
    AUTH0_API_CLIENT_ID = "6dB5tu7LBweT0dVfBim26FxgA9hsYCMS"
    AUTH0_API_CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.environ.get('DATABASE_USERNAME')}:{os.environ.get('DATABASE_PASSWORD')}"
        f"@{os.environ.get('DATABASE_HOST')}:5432/{os.environ.get('DATABASE_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def init_app(self, app):
        import logging
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)


class DevelopmentConfig(Config):
    S3_POST_IMAGE_BUCKET = "giare-test-post-image"
    S3_PROFILE_IMAGE_BUCKET = "giare-test-profile-image"


class ProductionConfig(Config):
    POSTS_PER_PAGE = 50
    S3_IMAGE_BUCKET = "hanggiamgia"


config = {
    "default": DevelopmentConfig(),
    "development": DevelopmentConfig(),
    "production": ProductionConfig()
}