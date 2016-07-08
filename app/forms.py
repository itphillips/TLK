#imports 'form' class
from flask.ext.wtf import Form
#imports required form field classes 
from wtforms import StringField, BooleanField, TextAreaField, SubmitField, HiddenField, RadioField, SelectField
#imports validator function 'DataRequired' - can be attached to field to perform 
#validation on data submitted by user
from wtforms.validators import DataRequired, Length

#defines subclass form 'loginform' from base class 'form'
#the subclass defines the fields of the form and the class variables
class LoginForm(Form):
	#users will login with OpenID (need Yahoo account?, or switch to OAuth?)
	openid = StringField('openid', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)


class EnterSentenceForm(Form):
	sentence = StringField('sentence', validators=[DataRequired()])
	# sentence_type = StringField('sentence', validators=[DataRequired()])
	language = StringField('language', validators=[DataRequired()])
	english_gloss = StringField('english_gloss', validators=[DataRequired()])
	# collection_date = StringField('sentence', validators=[DataRequired()])
	# collection_location = StringField('sentence', validators=[DataRequired()])
	# notes = TextAreaField('notes', validators=[Length(max=400)])

# class ShowSentenceForm(Form):
# 	sentence = SubmitField('sentence')
# 	user = HiddenField('user')
# 	language = HiddenField('language')
# 	user_id = HiddenField('user_id')


class TagPOSForm(Form):
	word = StringField('word', validators=[DataRequired()])
	# partofspeech = StringField('partofspeech', validators=[DataRequired()])
	partofspeech = SelectField('partofspeech', choices = 
							[('adjective','adjective'),
							('adverb','adverb'),
							('conjunction','conjunction'),
							('complementizer','complementizer'),
							('determiner','determiner'),
							('noun','noun'),
							('preposition','preposition'),
							('pronoun','pronoun'),
							('verb-auxiliary','verb-auxiliary'),
							('verb-copula','verb-copula'),
							('verb-ditransitive','verb-ditransitive'),
							('verb-intransitive','verb-intransitive'),
							('verb-transitive','verb-transitive'),
							('verb-sentential_complement','verb-sentential complement')])

	# partofspeech = RadioField('partofspeech', choices = 
	# 					[('adjective','Adjective'),
	# 					('adverb','adverb'),
	# 					('conjunction','conjunction'),
	# 					('complementizer','complementizer'),
	# 					('determiner','determiner'),
	# 					('noun','noun'),
	# 					('preposition','preposition'),
	# 					('pronoun','pronoun'),
	# 					('verb-auxiliary','verb-auxiliary'),
	# 					('verb-copula','verb-copula'),
	# 					('verb-ditransitive','verb-ditransitive'),
	# 					('verb-intransitive','verb-intransitive'),
	# 					('verb-transitive','verb-transitive'),
	# 					('verb-sentential_complement','verb-sentential complement')])

