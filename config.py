import os


class Config:
    def __init__(self):
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

    def init_app(self, app):
        import logging
        from logging import StreamHandler
        log_handler = StreamHandler()
        log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s %(threadName)s : %(message)s')
        log_handler.setFormatter(formatter)
        app.logger.addHandler(log_handler)


class DevelopmentConfig(Config):
    S3_IMAGE_BUCKET = "hanggiamgia"

class ProductionConfig(Config):
    POSTS_PER_PAGE = 50
    S3_IMAGE_BUCKET = "hanggiamgia"


config = {
    "default": DevelopmentConfig(),
    "development": DevelopmentConfig(),
    "production": ProductionConfig()
}