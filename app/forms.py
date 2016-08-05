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


#imports 'form' class
from flask.ext.wtf import Form
#imports required form field classes 
from wtforms import StringField, BooleanField
#imports validator function 'DataRequired' - can be attached to field to perform 
#validation on data submitted by user
from wtforms.validators import DataRequired

#defines subclass form 'loginform' from base class 'form'
#the subclass defines the fields of the form and the class variables
class LoginForm(Form):
	#users will login with OpenID 
	openid = StringField('openid', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)


