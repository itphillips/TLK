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


