import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir

#creates application object of class Flask
#here 'app' is a variable name
app = Flask(__name__)
#tells Flask to read and use configurations in config.py file
app.config.from_object('config')
app.config.from_object('privateconfigtwo') #privateconfig


#initializes database - the db object instantiated from clas SQLAlchemy represents
#the database and provides access to all the functionality of Flask_SQLAlchemy
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

#flask-openid extension requires a path to a tmp folder where files can be stored
oid = OpenID(app, os.path.join(basedir, '/tmp'))


#imports views module, which imports the 'app' variable defined above
#imports models module, which contains database structures
#here 'app' is a package
from app import viewstwo, modelstwo #views, models
#imports the named tables from modelstwo.py
from modelstwo import User, Sentence, Word, Words_sentence, Phrase, Phrases_sentence, Words_phrase, Users_sentence, Words_case

