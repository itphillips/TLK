#a model is a python class with attributes that match the columns of a corresponding 
#database table
#NEVER RENAME AN EXISTING FIELD OR MODEL -- instead, add a new field or model
from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
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
	sentences = db.relationship('Sentence', backref='users', lazy='dynamic', cascade="delete")
	words = db.relationship('Word', backref='users', cascade='delete')
	phrases = db.relationship('Phrase', backref='users', cascade='delete')
	gram_functions = db.relationship('Gram_function', backref='users', cascade='delete')

	
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
	sessionid = db.Column(db.String(40))
	sessionnumber = db.Column(db.Integer)
	sentence = db.Column(db.String)
	sentence_type = db.Column(db.String(30))
	sentence_language = db.Column(db.String(50))
	english_gloss = db.Column(db.String)
	collection_date = db.Column(db.DateTime)
	collection_location = db.Column(db.String(70))
	notes = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
	# words = db.relationship('Word', backref='sentences', cascade='delete')
	# word_sentence_positions = db.relationship('Word_sent_position', backref='sentences', cascade='delete')
	# phrases = db.relationship('Phrase', backref='sentences', cascade='delete')
	# word_phrase_positions = db.relationship('Word_phrase_position', backref='sentences', cascade='delete')
	# phrase_sentence_positions = db.relationship('Phrase_sentence_position', backref='sentences', cascade='delete')
	# gram_functions = db.relationship('Gram_function', backref='sentences', cascade='delete')

	def __repr__(self):
		return '<Sentence %r>' % (self.sentence)


class Word(db.Model):
	__tablename__ = 'words'
	id = db.Column(db.Integer, primary_key = True)
	word = db.Column(db.String(60))
	pos = db.Column(db.String(40))
	ws_linear_position = db.Column(db.Integer)
	id_sentence = db.Column(db.Integer, db.ForeignKey('sentences.id', ondelete="CASCADE"))
	id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
	# words = db.relationship('Word_sent_position', cascade='delete')
	# word_phrase_positions = db.relationship('Word_phrase_position', cascade='delete')

	def __repr__(self):
		return '<Word %r>' % (self.word)



class Phrase(db.Model):
	__tablename__ = 'phrases'
	id = db.Column(db.Integer, primary_key = True)
	phrase = db.Column(db.String(120))
	phrase_type = db.Column(db.String(60))
	id_sentence = db.Column(db.Integer, db.ForeignKey('sentences.id', ondelete="CASCADE"))
	id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
	# word_phrase_positions = db.relationship('Word_phrase_position', cascade='delete')
	# phrase_sentence_positions = db.relationship('Phrase_sentence_position', cascade='delete')
	# gram_functions = db.relationship('Gram_function', cascade='delete')

	def __repr__(self):
		return '<Phrase %r>' % (self.phrase)


#this will serve as the association table for words and phrases
class Word_phrase_position(db.Model):
	__tablename__ = 'word_phrase_positions'
	id = db.Column(db.Integer, primary_key = True)
	wp_linear_position = db.Column(db.Integer)
	id_word = db.Column(db.Integer, db.ForeignKey('words.id', ondelete="CASCADE"))
	id_sentence = db.Column(db.Integer, db.ForeignKey('sentences.id', ondelete="CASCADE"))
	id_phrase = db.Column(db.Integer, db.ForeignKey('phrases.id', ondelete="CASCADE"))

	def __repr__(self):
		return '<Word_phrase_position %r>' % (self.wp_linear_position)



class Phrase_sentence_position(db.Model):
	__tablename__ = 'phrase_sentence_positions'
	id = db.Column(db.Integer, primary_key = True)
	ps_linear_position = db.Column(db.Integer)
	id_phrase = db.Column(db.Integer, db.ForeignKey('phrases.id', ondelete="CASCADE"))
	id_sentence = db.Column(db.Integer, db.ForeignKey('sentences.id', ondelete="CASCADE"))

	def __repr__(self):
		return '<Phrase_sentence_position %r>' % (self.ps_linear_position)



class Gram_function(db.Model):
	__tablename__ = 'gram_functions'
	id = db.Column(db.Integer, primary_key = True)
	gram_function = db.Column(db.String(60))
	id_phrase = db.Column(db.Integer, db.ForeignKey('phrases.id', ondelete="CASCADE"))
	id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
	id_sentence = db.Column(db.Integer, db.ForeignKey('sentences.id', ondelete="CASCADE"))

	def __repr__(self):
		return '<Gram_function %r>' % (self.gram_function)


class Phrase_structure_rule(db.Model):
	__tablename__ = 'phrase_structure_rules'
	id = db.Column(db.Integer, primary_key = True)
	phrase_structure = db.Column(db.String(60))
	id_phrase = db.Column(db.Integer, db.ForeignKey('phrases.id', ondelete="CASCADE"))
	id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
	id_sentence = db.Column(db.Integer, db.ForeignKey('sentences.id', ondelete="CASCADE"))

	def __repr__(self):
		return '<Phrase_structure_rule %r>' % (self.phrase_structure_rule)


