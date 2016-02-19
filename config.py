import os
basedir = os.path.abspath(os.path.dirname(__file__))

#defines list of OpenID providers to present to users
OPENID_PROVIDERS = [
	{'name': 'Yahoo', 'url': 'https://me.yahoo.com'}]

#where SQLAlchemy-migrate files are stored
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


#enables automatic commits of database changes at the end of each request
SLALCHEMY_COMMIT_ON_TEARDOWN = True


