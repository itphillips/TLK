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


#!tlkenv/bin/python
#this script creates a new db according to the db information specified in config.py
#in terminal, first run chmod a+x db_create.py, then type ./db_create.py to run the script
#all of the below actions can be accomplished using flask-migrate command line tools
from migrate.versioning import api
from privateconfig import SQLALCHEMY_DATABASE_URI 
from config import SQLALCHEMY_MIGRATE_REPO
from app import db
import os.path
db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
	api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
	api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
	api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
