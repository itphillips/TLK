
#imports the app variable from the app package
from app import app, db, lm, oid 
from flask import Flask, render_template, url_for, request, redirect, jsonify, flash, session, g
import string
import psycopg2
import collections
import urlparse
from psycopg2 import extras
from flask.ext.login import login_user, logout_user, current_user, login_required
#imports class 'LoginForm' from forms.py
from .forms import LoginForm, EnterSentenceForm, TagPOSForm
#from .models import User, Sentence, Word
from .modelstwo import User, Sentence, Word, Word_sent_position, Phrase, Word_phrase_position, Gram_function

conn = psycopg2.connect('postgresql://ianphillips@localhost/tlktwo')
conn.set_session(autocommit=True)
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#this function loads a user from the db and is used by flask-login
@lm.user_loader #this decorator registers the function with flask-login
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user

@app.route('/')
@app.route('/home')
def home():
	return render_template("home.html",
							title='Home')

#view function that renders the login template by passing the form object LoginForm(Form)
#to the template login.html
#methods arguments tell Flask that this view function accespts GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler #tells flask-openid that htis is our login view function
def login():
	#this sees if the user is logged in, if so it won't do a second login
	#g global is set up by flask as a place to store and share data during the life
	#of a request - this stores the logged in user
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('user', username=g.user.username))
	#instantiated object from LoginForm()
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data #stores the value of 
		#remember_me boolean in flask session (not db.session!)
		#once data is stored in the session object, it will be avaialble during 
		#that request and any future requests made by the same client
		#data remains there until explicitly removed - flask keeps a different
		#session container for each client of the app

		#this triggers user authentication through flask-openid
		#takes 2 arguments: openid given by user in web form and a list of 
		#data items we want from openid provider
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])

		# flash('Login requested for OpenID="%s", remember_me=%s' %
		# 	(form.openid.data, str(form.remember_me.data)))
		# return redirect('/home')

	return render_template('login.html',
							title='Sign In',
							form=form,
							#grabs configuration by looking it up in app.config with 
							#its key, then adds array to render_template call as a 
							#template argument
							providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp): #resp argument contains information returned by openid provider
	#this if statement is for validation
	#user cannot login if email is not provided
	if resp.email is None or resp.email == "":
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email=resp.email).first()

	#searches db for email provided - adds new user to db if email is not found
	if user is None:
		username = resp.nickname
		if username is None or username == "":
			username = resp.email.split('@')[0]
		user = User(username=username, email=resp.email)
		db.session.add(user)
		db.session.commit()
	remember_me = False

	#loads remember_me value from flask session (stored in login view function)
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)

	#registers that this is a valid login
	login_user(user, remember = remember_me)

	#redirects to 'next' page or user-specific homepage, if next page not provided by request
	#next, meaning the page the user wants to see after logging in (e.g., they tried
	#to visit a user-specific page, but were stopped b/c they need to be logged in; 
	#after logging in, this page should appear)
	return redirect(request.args.get('next') or url_for('user', username=g.user.username))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route('/user/<username>')
@login_required #ensures this page is only seen by logged in users
def user(username): #'username' gets passed from after_login(), =g.user.username
	#this is SQLalchemy version
	#user = User.query.filter_by(username=username).first()
	
	dict_cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
	userID = dict_cur.fetchone()
	#returns list containing users.id as the only element
	
	dict_cur.execute("SELECT username FROM users WHERE username = %s;", (username,))
	user = dict_cur.fetchone()
	#returns list containing users.username as the only element
	
	if user == None:
		flash('User %s not found.', (username))
		return redirect(url_for('login'))

	else:
		try:
			dict_cur.execute("SELECT * FROM sentences INNER JOIN users ON users.id = sentences.id_user WHERE users.id = %s;", (userID[0],))
			sentences = dict_cur.fetchall()
			print sentences[0]
		except Exception as e:
			print e

		return render_template('usertwo.html',
								user=user[0],
								sentences=sentences,
								userID=userID[0])

@app.route("/input")
@login_required
def input_sentence():
	userID=request.args.get("userID")
	return render_template("input_sentencetwo.html", 
							userID=userID)

@app.route("/sentence")
@login_required
def confirm_sentence():
	try:
		userID=request.args.get("userID")
		sentence=request.args.get("sentence")
		language=request.args.get("language")
		date=request.args.get("date")
		paraphrase=request.args.get("paraphrase")
		sentence_type=request.args.get("sentence_type")
		sessionID=date+language
	except Exception as e:
		print e

	try:
		dict_cur.execute("SELECT sessionnumber FROM sentences INNER JOIN users ON users.id=sentences.id_user WHERE users.id = %s AND sessionid = %s;", (userID, sessionID))
		sessionnumber = dict_cur.fetchall()	
	except Exception as e:
		print e
	if dict_cur.fetchall() != []:
		sessionnumber=sessionnumber+1
	else:
		sessionnumber=1	
	try:
		#make sure that this sentence isn't already in the database
		dict_cur.execute("INSERT INTO sentences (sentence, sentence_language, collection_date, sessionnumber, sessionid, english_gloss, id_user, sentence_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(sentence, language, date, sessionnumber, sessionID, paraphrase, userID, sentence_type))
		# dict_cur.execute("SELECT id FROM sentences WHERE sentence = '{}' AND collection_date = '{}' AND sessionID = '{}';".format (sentence, date, sessionID) )
		# sentenceID = dict_cur.fetchone()[0]
	except Exception as e:
		print e
		#return redirect to same page with error message==make sure you fill in all fields.
	#continued_session=request.args.get("continued_session")
	print "done confirm_sentence"
	return redirect(url_for('user',
							username=g.user.username))


@app.route('/delete/<int:sent_id>')
@login_required
def delete(sent_id):
	# sentence = Sentence.query.get(sent_id)
	dict_cur.execute("SELECT * FROM sentences WHERE id = %s;", (sent_id,))
	sentence = dict_cur.fetchone()
	# print "this is id", sent_id
	# print "this is sentence", sentence

	if sentence is None:
		flash('Sentence not found!')
		return redirect(url_for('user', 
								username=g.user.username))
	# if userID != g.user.id:
	# 	flash('You cannot delete this sentence!')
	# 	return redirect(url_for('user', 
	# 							username=g.user.username))

	dict_cur.execute("DELETE FROM sentences WHERE sentences.id = %s", (sent_id,))	
	dict_cur.execute("DELETE FROM words WHERE words.id_sentence = %s", [sent_id])
	dict_cur.execute("DELETE FROM phrases WHERE phrases.id_sentence = %s", [sent_id])
	dict_cur.execute("DELETE FROM word_phrase_positions WHERE word_phrase_positions.id_sentence = %s", [sent_id])
	dict_cur.execute("DELETE FROM word_sentence_positions WHERE word_sentence_positions.id_sentence = %s", [sent_id])
	return redirect(url_for('user', 
							username=g.user.username))


@app.route("/tagPOS")
@login_required
def tag_pos():
	error= request.args.get("error")
	sentence = request.args.get("sentence")
	userID = request.args.get("userID")
	language=request.args.get("sentence_language")
	sentenceID=request.args.get("sentenceID")

	print "all done tag pos"
	return render_template("tag_words2.html", 
							sentence=sentence, 
							userID=userID, 
							sentenceID=sentenceID, 
							error=error, 
							language=language)

@app.route("/confirmPOS")
@login_required
def pos_confirm():
	sentence=request.args.get("sentence")
	userID = request.args.get("userID")
	sentenceID = request.args.get("sentenceID")
	language = request.args.get("language")
	pos = ""
	
	for i in range(len(sentence.split())):
		if request.args.get(str(i)):
			try:
				pos=pos+(request.args.get(str(i)))+" "
			except Exception as e:
				print e
		else:
			print "error"
			return redirect(url_for('tag_pos', 
									sentence=sentence, 
									userID=userID, 
									sentenceID=sentenceID, 
									error= 1, 
									language=language))
	print "done pos confirm"
	return render_template("POS_confirmtwo.html", 
							sentence=sentence, 
							userID=userID, 
							sentenceID=sentenceID, 
							pos=pos, 
							language=language)

@app.route("/group")
@login_required
def group():
	print request.args
	redo = request.args.get("redo")
	print redo, "redo"
	userID = request.args.get("userID")
	sentenceID = request.args.get("sentenceID")
	sentence = request.args.get("sentence")

	wordlist = sentence.split()
	for word in wordlist:
		wordlinposition = 1 + wordlist.index(word)
		
	print wordlinposition
	
	if redo == None:
		language=request.args.get("language")
		pos_array = str(request.args.get("pos")).split()
		words = sentence.split()
		for i in range(len(words)):
			try:
				dict_cur.execute("SELECT id from words WHERE word = '{}' AND pos = '{}' AND language = '{}';".format(words[i], pos_array[i], language))
				found_words = dict_cur.fetchall()
				print found_words, "found words"
				if found_words == []:
					dict_cur.execute("INSERT INTO words (word, pos, language, sentenceid) VALUES (%s, %s, %s, %s)", (words[i], pos_array[i], language, sentenceID))
					dict_cur.execute("SELECT id from words WHERE word = '{}' AND pos = '{}' AND language = '{}';".format(words[i], pos_array[i], language))
					found_words = dict_cur.fetchall()
				wordID = found_words[0]["id"]
				dict_cur.execute("SELECT id from words_sentences WHERE wordID = '{}' AND sentenceID = '{}';".format(wordID, sentenceID))
				found_words_sentences=dict_cur.fetchall()
				if found_words_sentences == []:
					dict_cur.execute("INSERT INTO words_sentences (wordID, sentenceID, position) VALUES (%s, %s, %s)", (wordID, sentenceID, i))
			except Exception as e:
				print e

	return render_template("grouptwo.html", 
							sentence=sentence, 
							userID=userID, 
							sentenceID=sentenceID)

@app.route("/tag_phr_struct")
@login_required
def tag_phrase_structure():
	print "hi"
	sentence= request.args.get("sentence")
	words=sentence.split()
	userID = request.args.get("userID")
	sentenceID=request.args.get("sentenceID")
	print sentenceID, "sentenceID"
	redo = request.args.get("redo")
	print redo
	if redo=="True":
		print "redo true"
		word_positions_in_phrase_string= request.args.get("word_positions_in_phrase")
	else:
		word_positions_in_phrase_string = request.args.get("phrase")
		print word_positions_in_phrase_string, "phrase"

	word_positions_in_phrase = word_positions_in_phrase_string.split()
	print word_positions_in_phrase, "word_positions_in_phrase"
	
	phrase=" ".join([str(words[int(word_position)]) for word_position in word_positions_in_phrase])
	print phrase, "phrase"
	phrase_type = request.args.get("phrase_type")
	print phrase_type
	phrase_type_dict = {"S":[("NP", "necessary"), ("VP", "necessary")], "NP": [("det","optional"), ("AP", "optional"), ("N","necessary"), ("PP","optional")], "VP":[("V","necessary"), ("PP","optional"), ("NP","optional"), ("NP2", "optional"), ("S","optional"), ("CP", "optional"), ("AP","optional"), ("PP2","optional")], "PP":[("P","necessary"), ("NP","optional") ,("PP","optional")], "AP":[("deg","optional"), ("A","necessary")], "CP": [("C","necessary"), ("S","necessary")] }

	phrase_structure_options=phrase_type_dict[phrase_type]
	print phrase_structure_options, "phrase_structure_options"
	return render_template("tag_phrase_structure.html", sentence=sentence, userID=userID, phrase=phrase, phrase_type=phrase_type, phrase_structure_options=phrase_structure_options, sentenceID=sentenceID, word_positions_in_phrase=word_positions_in_phrase_string)

@app.route("/confirm_phrase")
@login_required
def confirm_phrase():
	phrase_structure=request.args.get("phrase_structure")
	sentence= request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	userID = request.args.get("userID")
	phrase_type = request.args.get("phrase_type")
	phrase=request.args.get("phrase")
	word_positions_in_phrase=request.args.get("word_positions_in_phrase")
	print word_positions_in_phrase, "word_positions_in_phrase"
	print phrase, "phrase"
	print phrase_structure, "phrase_structure"
	return render_template("confirm_phrase.html", sentence=sentence, userID=userID, phrase=phrase, phrase_type=phrase_type, phrase_structure=phrase_structure, sentenceID=sentenceID, word_positions_in_phrase=word_positions_in_phrase)

@app.route("/phr_to_database")
@login_required
def put_phrase_in_database():
	print "hi"
	phrase_structure=request.args.get("phrase_structure")
	sentence= request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	userID = request.args.get("userID")
	phrase_type = request.args.get("phrase_type")
	phrase=request.args.get("phrase")
	word_positions_in_phrase=request.args.get("word_positions_in_phrase")
	print word_positions_in_phrase
	print "prh in database "
	#should check if this phrase is already in the database and notify user
	try: 
		dict_cur.execute("INSERT INTO phrases (phrase, phrase_type, phrase_subtype, sentenceid) VALUES (%s, %s, %s, %s)", (phrase, phrase_type, phrase_structure, sentenceID))
	except Exception as e:
		print e
	print "insert phrases"

	try:
		dict_cur.execute("SELECT id from phrases WHERE phrase = '{}' AND phrase_type = '{}' AND phrase_subtype = '{}';".format(phrase, phrase_type, phrase_structure))
	except Exception as e:
		print e
	print "select from phrases"
	phraseID=dict_cur.fetchall()[0][0]

	#should also check to see if this is in phrases_sentences
	try:
		dict_cur.execute("INSERT INTO phrases_sentences (phraseID, sentenceID) VALUES (%s, %s)", (phraseID, sentenceID))
	except Exception as e:
		print e
	print "insert into phrases_sentences"

	try:
		dict_cur.execute("SELECT position,wordID from words_sentences WHERE sentenceID = '{}';".format(sentenceID))
		wordIDPairs= dict_cur.fetchall()
	except Exception as e:
		print e
	print "select id pairs"
	wordIDPairs.sort(key=lambda x: int(x[1]))
	print wordIDPairs,"wordIDPairs"
	wordIDs=[wordID[1] for wordID in wordIDPairs]
	print wordIDs, "wordIDs"
	print word_positions_in_phrase, "word_positions_in_phrase"
	print type(word_positions_in_phrase)
	word_positions_in_phrase=word_positions_in_phrase.split()
	try:
		word_ids_in_phrase = [wordIDs[int(position)] for position in word_positions_in_phrase]
	except Exception as e:
		print e
	print word_ids_in_phrase, "word_ids_in_phrase"
	#anddd check to see if they're in words_phrases. They probably are if they're in one of the others...need to reason about this]
	for i in range(len(word_ids_in_phrase)):
		try:
			dict_cur.execute("INSERT INTO words_phrases (wordID, phraseID, position, sentenceid) VALUES (%s, %s, %s, %s)", (wordIDs[i], phraseID, i, sentenceID))
		except Exception as e:
			print e
	print "hi"
	return redirect(url_for('group', redo=False, sentence=sentence, sentenceID=sentenceID, userID=userID))

@app.route("/tagSubj")
@login_required
def tag_subj():
	sentence=request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	words = []
	try:
		dict_cur.execute("SELECT position,wordID from words_sentences WHERE sentenceID = '{}';".format(sentenceID))
		wordIDs= dict_cur.fetchall()
	except Exception as e:
		print e
	wordIDs.sort(key=lambda x: int(x[1]))
	wordIDs=[wordID[1] for wordID in wordIDs]
	wordIDString=""
	for wordID in wordIDs:
		print wordID
		try:
			dict_cur.execute("SELECT word from words WHERE id ='{}';".format(wordID))
		except Exception as e:
			print e
		word=dict_cur.fetchall()
		print word
		words.append(word[0][0])
		print words
		wordIDString=wordIDString+str(wordID)+" "
		print wordIDString
	print words
	return render_template("tag_subj.html", words=words, sentence=sentence, wordIDs=wordIDs, wordIDString=wordIDString)

@app.route("/confirm_subj")
@login_required
def confirm_subj():
	print "confirm_subj"
	sentence=request.args.get("sentence")
	wordIDString=request.args.get("wordIDString")
	word_IDs_of_subject_string=request.args.get("subject")
	word_IDs_of_subject_list=word_IDs_of_subject_string.split()
	words_of_subject=""
	for wordID in word_IDs_of_subject_list:
		print wordID
		print type(wordID)
		try:
			dict_cur.execute("SELECT word from words WHERE id ='{}';".format(int(wordID)))
			first_result=dict_cur.fetchall()[0]
			print first_result
			words_of_subject= words_of_subject+(str(first_result[0]))+" "
		except Exception as e:
			print e
	print "oy"

	return render_template("confirm_subj.html", subject=words_of_subject, sentence=sentence, wordIDs=request.args.get("wordIDString"), word_IDs_of_subject=word_IDs_of_subject_string, wordIDString=wordIDString)

@app.route("/tag_obj")
@login_required
def tag_obj():
	sentence=request.args.get("sentence")
	print sentence
	wordIDString=request.args.get("wordIDString")
	print wordIDString
	redo=request.args.get("redo")
	if redo !="yes":
		word_IDs_of_subject=request.args.get("subject").split()
		print word_IDs_of_subject
		for wordID in word_IDs_of_subject:
			try:
				dict_cur.execute("SELECT * from words_cases WHERE wordID ='{}' AND gram_case='N';".format(wordID))
				words_in_words_cases = dict_cur.fetchall()
			except Exception as e:
				print e
			print wordID
			print words_in_words_cases
			if words_in_words_cases == []:
				try:
					dict_cur.execute("INSERT INTO words_cases (wordID, gram_case) VALUES (%s, %s)", (wordID, "N"))
				except Exception as e:
					print e
			print wordID
	return render_template("tag_obj.html", sentence=sentence, wordIDString=wordIDString, wordIDs=wordIDString.split(), words=sentence.split())

@app.route("/confirm_obj")
@login_required
def confirm_obj():
	print "confirm_obj"
	sentence=request.args.get("sentence")
	wordIDString=request.args.get("wordIDString")
	DOIOstring=request.args.get("object")
	DOIOlist=DOIOstring.replace("DO","").split("IO")
	DO=DOIOlist[0]
	IO=DOIOlist[1]
	if DO != "_":
		DO=DO.replace("_","")
		DOList=DO.split()
	if IO != "_":
		IO=IO.replace("_","")
		IOList=IO.split()
	print DOList, "do list"
	print IOList, "io list"
	DOWords=""
	IOWords=""
	confirm_needed=False
	if IOList:
		confirm_needed=True
		for wordID in IOList:
			print wordID
			dict_cur.execute("SELECT word from words WHERE id ='{}';".format(wordID))
			print "ok"
			IOWords= IOWords+(str(dict_cur.fetchall()[0][0]))+" "
			print IOWords
	print 'hi'
	if DOList:
		confirm_needed=True
		for wordID in DOList:
			print wordID
			dict_cur.execute("SELECT word from words WHERE id ='{}';".format(wordID))
			print "ok"
			DOWords= DOWords+(str(dict_cur.fetchall()[0][0]))+" "
			print DOWords
	print DO,"DO"
	print IO,"IO"
	if confirm_needed:
		return render_template("confirm_obj.html", DO=DO, IO=IO, sentence=sentence, wordIDs=request.args.get("wordIDString"), wordIDString=wordIDString, DOWords=DOWords, IOWords=IOWords)
	return redirect(url_for("prompt_new_sentence"))

@app.route("/end")
@login_required
def prompt_new_sentence():
	DO=request.args.get("DO")
	IO=request.args.get("IO")
	wordIDs=request.args.get("wordIDString").split()
	if DO:
		for wordID in DO.split():
			try:
				dict_cur.execute("SELECT * from words_cases WHERE wordID ='{}' AND gram_case='ACC';".format(wordID))
				words_in_words_cases = dict_cur.fetchall()
			except Exception as e:
				print e
			print wordID
			print words_in_words_cases
			if words_in_words_cases == []:
				try:
					dict_cur.execute("INSERT INTO words_cases (wordID, gram_case) VALUES (%s, %s)", (wordID, "ACC"))
				except Exception as e:
					print e
			print wordID		
	if IO:
		for wordID in IO.split():
			try:
				dict_cur.execute("SELECT * from words_cases WHERE wordID ='{}' AND gram_case='DAT';".format(wordID))
				words_in_words_cases = dict_cur.fetchall()
			except Exception as e:
				print e
			print wordID
			print words_in_words_cases
			if words_in_words_cases == []:
				try:
					dict_cur.execute("INSERT INTO words_cases (wordID, gram_case) VALUES (%s, %s)", (wordID, "DAT"))
				except Exception as e:
					print e
			print wordID		

	return render_template("prompt_new_sentence.html")

