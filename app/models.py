#a model is a python class with attributes that match the columns of a corresponding 
#database table
#NEVER RENAME AN EXISTING FIELD OR MODEL -- instead, add a new field or model
from app import db
from sqlalchemy.dialects.postgresql import JSON
# from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
	#each of these is a class variable
	#this defines the name of the table in the database (the convention is to use
	#plurals for table names)
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	#this is not an acutal db field - for a one-to-many relationship, this is defined
	#on the 'one' side - the first argument indicates the 'many' class of the
	#relationship - not sure if this need to be the table name or class name
	#backref defines a field that will be added to the objects of the 'many' class
	#that points back at the 'one' object
	sentences = db.relationship('Sentence', backref='author', lazy='dynamic')

	
	#this should just return true unless the object represents a user that should not
	#be allowed to authenticate for some reason
	def is_authenticated(self):
		return True

	#should return true for users unless they are incactive (e.g., becuase they've 
	#been banned)
	def is_active(self):
		return True

	#should return true only for fake users
	def is_anonymous(self):
		return False

	#should return a unique identifier for user in unicode - we use the unique id
	#generated by the db layer for this - two alternatives are presented b/c unicode
	#is handled differently in p2 and p3
	def get_id(self):
		try:
			return unicode(self.id) #python 2
		except NameError:
			return str(self.id) #python 3

	#tells python how to print objects of this class
	def __repr__(self):
		return '<User %r>' % (self.username)

class Sentence(db.Model):
	__tablename__ = 'sentences'
	id = db.Column(db.Integer, primary_key = True)
	sessionID = db.Column(db.String(3))
	session_number = db.Column(db.Integer)
	sentence = db.Column(db.String(90))
	sentence_type = db.Column(db.String(30))
	language = db.Column(db.String(25))
	english_gloss = db.Column(db.String(140))
	# collection_date = db.Column(db.String(70))
	collection_location = db.Column(db.String(70))
	notes = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	

	def __repr__(self):
		return '<Sentence %r>' % (self.sentence)

class Word(db.Model):
	__tablename__ = 'words'
	id = db.Column(db.Integer, primary_key = True)
	word = db.Column(db.String(30))
	partofspeech = db.Column(db.String(30))
	#gram_case = db.Column(db.String(30))
	sentence_id = db.Column(db.Integer)
	# language_id = db.Column(db.Integer, db.ForeignKey('sentences.language'))

	def __repr__(self):
		return '<Word %r>' % (self.word)
