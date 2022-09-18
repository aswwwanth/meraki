import os

class Config(object):
    POSTGRES = {
        'user': os.environ.get('db_user'),
        'pw': os.environ.get('db_password'),
        'db': os.environ.get('db_name'),
        'host': os.environ.get('db_host'),
        'port': os.environ.get('db_port'),
    }
    
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'meraki2020*'