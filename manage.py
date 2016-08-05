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


##on 9/6/15, i put the "Manage" functionality into TLK.py--this script is no longer necessary
from flask.ext.script import Manager
from app import app

manager = Manager(app)
app.config['DEBUG'] = True # Ensures debugger will load

if __name__ == '__main__':
	manager.run()