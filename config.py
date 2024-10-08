class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:durka@localhost/web-site-for-remember-formulas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret_key'
