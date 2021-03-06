# The Linguist's Kitchen: A web-based app for learning linguistics
# Copyright (C) 2016 Ian Phillips

# This file is part of The Linguist's Kitchen.

# The Linguist's Kitchen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# The Linguist's Kitchen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Linguist's Kitchen.  If not, see <http://www.gnu.org/licenses/>.


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
app.config.from_object('privateconfig')


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
from app import views, models
#imports the named tables from models.py
from models import User, Sentence, Word, Phrase, Word_phrase_position, Gram_function, Phrase_structure_rule

