import os

class Config(object):
    POSTGRES = {
        'user': 'meraki',
        'pw': 'meraki2020*',
        'db': 'meraki',
        'host': 'db',
        'port': '5432',
    }
    
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'meraki2020*'