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
basedir = os.path.abspath(os.path.dirname(__file__))

#defines list of OpenID providers to present to users
OPENID_PROVIDERS = [
	{'name': 'Yahoo', 'url': 'https://me.yahoo.com'}]

#where SQLAlchemy-migrate files are stored
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


#enables automatic commits of database changes at the end of each request
SLALCHEMY_COMMIT_ON_TEARDOWN = True


