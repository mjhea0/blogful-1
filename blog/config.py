import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://action:action@localhost:5432/blogful"
    DEBUG = True
    SECRET_KEY = os.environ.get("BLOGFUL_SECRET_KEY", "")