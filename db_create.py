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
