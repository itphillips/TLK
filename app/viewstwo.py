
#imports the app variable from the app package
from app import app, db, lm, oid 
from flask import Flask, render_template, url_for, request, redirect, jsonify, flash, session, g
import string
import psycopg2
import collections
import urlparse
import ast
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

	dict_cur.execute("DELETE FROM word_phrase_positions WHERE word_phrase_positions.id_sentence = %s;", (sent_id,))
	dict_cur.execute("DELETE FROM word_sentence_positions WHERE word_sentence_positions.id_sentence = %s;", (sent_id,))
	dict_cur.execute("DELETE FROM phrase_sentence_positions WHERE phrase_sentence_positions.id_sentence = %s;", (sent_id,))
	dict_cur.execute("DELETE FROM gram_functions WHERE gram_functions.id_sentence = %s;", (sent_id,))
	dict_cur.execute("DELETE FROM words WHERE words.id_sentence = %s;", (sent_id,))
	dict_cur.execute("DELETE FROM phrases WHERE phrases.id_sentence = %s;", (sent_id,))
	dict_cur.execute("DELETE FROM sentences WHERE sentences.id = %s;", (sent_id,))	
	return redirect(url_for('user', 
							username=g.user.username))


@app.route("/tagPOS")
@login_required
def tag_pos():
	error= request.args.get("error")
	sentence = request.args.get("sentence")
	print sentence
	userID = request.args.get("userID")
	language=request.args.get("sentence_language")
	
	dict_cur.execute("SELECT id from sentences WHERE sentence = %s;", (sentence,))
	sentenceID = dict_cur.fetchone()[0]
	print "sentenceID for tagPOS = ", sentenceID

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
	print "sentenceID for confirmPOS = ", sentenceID
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
	print "this is sentenceID", sentenceID
	sentence = request.args.get("sentence")

# 	wordlist = sentence.split()
# 	for word in wordlist:
# 		wordlinposition = 1 + wordlist.index(word)
# 		
# 		print wordlinposition
	
	if redo == None:
		language=request.args.get("language")
		pos_array = str(request.args.get("pos")).split()
		words = sentence.split()
		for i in range(len(words)):
			try:
				dict_cur.execute("SELECT * FROM words INNER JOIN sentences ON words.id_sentence=sentences.id WHERE words.word = %s AND words.pos = %s AND sentences.sentence_language = %s;", (words[i], pos_array[i], language))
				found_words = dict_cur.fetchall()
				print found_words, "found words"
				if found_words == []:
					dict_cur.execute("INSERT INTO words (word, pos, id_sentence, id_user) VALUES (%s, %s, %s, %s);", (words[i], pos_array[i], sentenceID, userID))
					
					dict_cur.execute("SELECT id FROM words WHERE words.word = %s AND words.pos = %s AND words.id_sentence = %s AND words.id_user = %s;", (words[i], pos_array[i], sentenceID, userID))
					found_words = dict_cur.fetchall()
				wordID = found_words[0]["id"]
				dict_cur.execute("SELECT id FROM word_sentence_positions wsp WHERE wsp.id_word = %s AND wsp.id_sentence = %s;", (wordID, sentenceID))
				found_wsp = dict_cur.fetchall()
				if found_wsp == []:
					dict_cur.execute("INSERT INTO word_sentence_positions (id_word, id_sentence, ws_linear_position) VALUES (%s, %s, %s)", (wordID, sentenceID, i))
# 			print "word: %s wordID: %s sentenceID: %s ws position: %s" % (word, wordID, sentenceID, i)
			except Exception as e:
				print e

	return render_template("grouptwo.html", 
							sentence=sentence, 
							userID=userID, 
							sentenceID=sentenceID)


@app.route("/tag_phr_struct")
@login_required
def tag_phrase_structure():
	sentence = request.args.get("sentence")
	words = sentence.split()
	userID = request.args.get("userID")
	sentenceID = request.args.get("sentenceID")
	print sentenceID, "sentenceID"
	redo = request.args.get("redo")
	print redo
	
	if redo == "True":
		print "redo true"
		word_positions_in_phrase_string = request.args.get("word_positions_in_phrase")
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
	return render_template("tag_phrase_structure.html", 
							sentence=sentence, 
							userID=userID, 
							phrase=phrase, 
							phrase_type=phrase_type, 
							phrase_structure_options=phrase_structure_options, 
							sentenceID=sentenceID, 
							word_positions_in_phrase=word_positions_in_phrase_string)


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
	return render_template("confirm_phrase.html", 
							sentence=sentence, 
							userID=userID, 
							phrase=phrase, 
							phrase_type=phrase_type, 
							phrase_structure=phrase_structure, 
							sentenceID=sentenceID, 
							word_positions_in_phrase=word_positions_in_phrase)


@app.route("/phr_to_database")
@login_required
def put_phrase_in_database():
	phrase_structure=request.args.get("phrase_structure")
	sentence= request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	# userID = request.args.get("userID")
	# print "this is phr to db userID", userID
	username=g.user.username
	phrase_type = request.args.get("phrase_type")
	phrase=request.args.get("phrase")
	word_positions_in_phrase=request.args.get("word_positions_in_phrase")
	print word_positions_in_phrase
	print "prh in database "

	try:
		dict_cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
		userID = dict_cur.fetchone()[0]
		print type(userID), userID
	except Exception as e:
		print e

	try: 
		dict_cur.execute("INSERT INTO phrases (phrase, phrase_type, id_sentence, id_user) VALUES (%s, %s, %s, %s)", (phrase, phrase_type, sentenceID, userID))
	except Exception as e:
		print e
	print "inserted phrases"

	try:
		dict_cur.execute("SELECT id FROM phrases WHERE phrase = %s AND phrase_type = %s and id_user = %s;", (phrase, phrase_type, userID))
	except Exception as e:
		print e
	print "select from phrases"
	phraseID=dict_cur.fetchone()
	print phraseID, "phrase id"

	wordposlist = phrase.split()
	for item in wordposlist:
		position = wordposlist.index(item)
		dict_cur.execute("SELECT id FROM words WHERE word = %s AND id_sentence = %s AND id_user = %s;", (item, sentenceID, userID))
		wordID = dict_cur.fetchone()

		print "the id for '%s' is: %s" % (item, wordID[0])
		dict_cur.execute("INSERT INTO word_phrase_positions (wp_linear_position, id_word, id_sentence, id_phrase) VALUES (%s, %s, %s, %s);", (position, wordID[0], sentenceID, phraseID[0]))

	# Just commented these lines out on 3/22/16 - may need to uncomment them if it turns out they do something required later	
	# try:
	# 	dict_cur.execute("SELECT position, wordID from words_sentences WHERE sentenceID = '{}';".format(sentenceID))
	# 	wordIDPairs= dict_cur.fetchall()
	# except Exception as e:
	# 	print e
	# print "select id pairs"
	# wordIDPairs.sort(key=lambda x: int(x[1]))
	# print wordIDPairs,"wordIDPairs"
	# wordIDs=[wordID[1] for wordID in wordIDPairs]
	# print wordIDs, "wordIDs"
	# print word_positions_in_phrase, "word_positions_in_phrase"
	# print type(word_positions_in_phrase)
	# word_positions_in_phrase=word_positions_in_phrase.split()
	# try:
	# 	word_ids_in_phrase = [wordIDs[int(position)] for position in word_positions_in_phrase]
	# except Exception as e:
	# 	print e
	# print word_ids_in_phrase, "word_ids_in_phrase"
	# #anddd check to see if they're in words_phrases. They probably are if they're in one of the others...need to reason about this]
	# for i in range(len(word_ids_in_phrase)):
	# 	try:
	# 		dict_cur.execute("INSERT INTO words_phrases (wordID, phraseID, position, sentenceid) VALUES (%s, %s, %s, %s)", (wordIDs[i], phraseID, i, sentenceID))
	# 	except Exception as e:
	# 		print e
	# print "hi"
	return redirect(url_for('group', 
							redo=False, 
							sentence=sentence, 
							sentenceID=sentenceID, 
							userID=userID))


@app.route("/tagSubj")
@login_required
def tag_subj():
	error=request.args.get("error")
	sentence=request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	userID = request.args.get("userID")
	phrases = []
	try:
		dict_cur.execute("SELECT id, phrase FROM phrases WHERE id_sentence = %s;", (sentenceID,))
		phrases= dict_cur.fetchall()
	except Exception as e:
		print e
	# wordIDs.sort(key=lambda x: int(x[1]))
	# wordIDs=[wordID[1] for wordID in wordIDs]
	# wordIDString=""
	for phrase in phrases:
		print "id", phrase[0], "phrase: ", phrase[1]
	# 	try:
	# 		dict_cur.execute("SELECT word from words WHERE id ='{}';".format(wordID))
	# 	except Exception as e:
	# 		print e
	# 	word=dict_cur.fetchall()
	# 	print word
	# 	words.append(word[0][0])
	# 	print words
	# 	wordIDString=wordIDString+str(wordID)+" "
	# 	print wordIDString
	# print words
	return render_template("tag_subj.html", 
							phrases=phrases, 
							sentence=sentence,
							userID=userID,
							sentenceID=sentenceID,
							error=error
							)


@app.route("/confirm_subj")
@login_required
def confirm_subj():
	print "confirm_subj"
	gramfunc="subject"
	userID=request.args.get("userID")
	sentence=request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	subject=request.args.get("subject")
	subject_li=ast.literal_eval(subject)
	phraseID = subject_li[0]
	print userID
	print sentence
	print sentenceID
	print type(subject), subject
	print type(subject_li), subject_li, "subject id: ", phraseID


	try:
		dict_cur.execute("INSERT INTO gram_functions (gram_function, id_phrase, id_user, id_sentence) VALUES (%s, %s, %s, %s);", (gramfunc, phraseID, userID, sentenceID))
	except Exception as e:
		print e
	print "inserted grammmatical function"

	return redirect(url_for('tag_obj',
							userID=userID,
							sentence=sentence,
							sentenceID=sentenceID
							))


@app.route('/tag_obj/<userID>/<sentence>/<sentenceID>')
@login_required
def tag_obj(userID, sentence, sentenceID):
	phrases = []
	try:
		dict_cur.execute("SELECT id, phrase FROM phrases WHERE id_sentence = %s;", (sentenceID,))
		phrases= dict_cur.fetchall()
	except Exception as e:
		print e

	for phrase in phrases:
		print "id", phrase[0], "phrase: ", phrase[1]

	return render_template("tag_obj.html", 
							phrases=phrases, 
							sentence=sentence,
							userID=userID,
							sentenceID=sentenceID,
							)



@app.route("/confirm_obj")
@login_required
def confirm_obj():
	print "confirm_obj"
	gramfunc="direct object"
	userID=request.args.get("userID")
	sentence=request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	dobject=request.args.get("dobject")
	print type(dobject), dobject
	dobject_li=ast.literal_eval(dobject)
	phraseID = dobject_li[0]
	print userID
	print sentence
	print sentenceID
	print type(dobject), dobject
	print type(dobject_li), dobject_li, "direct object id: ", phraseID


	try:
		dict_cur.execute("INSERT INTO gram_functions (gram_function, id_phrase, id_user, id_sentence) VALUES (%s, %s, %s, %s);", (gramfunc, phraseID, userID, sentenceID))
	except Exception as e:
		print e
	print "inserted grammmatical function"

	return render_template('analyzed_sent.html',
							userID=userID,
							sentence=sentence,
							sentenceID=sentenceID
							)


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
				dict_cur.execute("SELECT * FROM words_cases WHERE wordID ='{}' AND gram_case='DAT';".format(wordID))
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

@app.route("/analyzed_sent")
@login_required
def analyzed_sent():
	error= request.args.get("error")	
	userID = request.args.get("userID")
	sentence = request.args.get("sentence")
	print "analyzed_sent", type(sentence), sentence
	language=request.args.get("sentence_language")


	try:
		dict_cur.execute("SELECT id FROM sentences WHERE sentence = %s;", (sentence,))
		sentenceID = dict_cur.fetchone()[0]


		dict_cur.execute("SELECT word, pos FROM words w INNER JOIN sentences s ON w.id_sentence=s.id WHERE s.id=%s ORDER BY w.id ASC;", (sentenceID,))
		POSlist = dict_cur.fetchall()


		dict_cur.execute("SELECT username FROM users WHERE id=%s;", (userID,))
		username = dict_cur.fetchone()[0]


		dict_cur.execute("SELECT sentence_type FROM sentences WHERE id = %s;", (sentenceID,))
		sent_type = dict_cur.fetchone()[0]


		dict_cur.execute("SELECT english_gloss FROM sentences WHERE id = %s;", (sentenceID,))
		english_gloss = dict_cur.fetchone()[0]


		dict_cur.execute("SELECT notes FROM sentences WHERE id = %s;", (sentenceID,))
		notes = dict_cur.fetchone()[0]


		dict_cur.execute("SELECT collection_date FROM sentences WHERE id = %s;", (sentenceID,))
		collection_date = dict_cur.fetchone()[0]

		dict_cur.execute("SELECT * FROM word_phrase_positions wpp INNER JOIN phrases p ON p.id=wpp.id_phrase WHERE p.id_sentence = %s AND wpp.wp_linear_position = 0 ORDER BY wpp.id_word ASC;", (sentenceID,))
		phrases = dict_cur.fetchall()

	except Exception as e:
		print e

	return render_template("analyzed_sent.html",
							username=userID,
							sentence=sentence,
							sentenceID=sentenceID,
							language=language,
							sent_type=sent_type,
							gloss=english_gloss,
							notes=notes, #there is no field to enter notes in the sentence input screen
							collection_date=collection_date,
							POSlist=POSlist,
							phrases=phrases
							)

