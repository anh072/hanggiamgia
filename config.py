import os


class Config:
    POSTS_PER_PAGE = 20
    COMMENTS_PER_PAGE = 20
    SLOW_DB_QUERY_TIME = 0.5
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def init_app(self, app):
        import logging
        from logging import StreamHandler
        log_handler = StreamHandler()
        log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s %(threadName)s : %(message)s')
        log_handler.setFormatter(formatter)
        app.logger.addHandler(log_handler)


class DevelopmentConfig(Config):
    pass

class ProductionConfig(Config):
    POSTS_PER_PAGE = 50


config = {
    "default": DevelopmentConfig(),
    "development": DevelopmentConfig(),
    "production": ProductionConfig()
}