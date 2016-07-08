
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
from .models import User, Sentence, Word, Phrase, Word_phrase_position, Phrase_sentence_position, Gram_function, Phrase_structure_rule

conn = psycopg2.connect('postgresql://ianphillips@localhost/tlk')
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
@app.route('/TLK')
def home():
	return render_template("home.html")

@app.route('/about')
def about():
	return render_template("about.html")

#view function that renders the login template by passing the form object LoginForm(Form)
#to the template login.html
#methods arguments tell Flask that this view function accespts GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler #tells flask-openid that this is our login view function
def login():
	#this sees if the user is logged in, if so it won't do a second login
	#g global is set up by flask as a place to store and share data during the life
	#of a request - this stores the logged in user
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('user', userID=g.user.id))
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
	print "\ng.user.username: ", g.user.username, type(g.user.username)
	print "\ng.user.id: ", g.user.id, type(g.user.id)
	return redirect(request.args.get('next') or url_for('user', userID=g.user.id))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route('/user/<userID>')
@login_required 
def user(userID): #'userID' gets passed from after_login(), =g.user.id
	print "\nthis is user function"
	# dict_cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
	# userID = dict_cur.fetchone()[0]
	userID = int(userID)
	print "userID: ", userID, type(userID)
	
	dict_cur.execute("SELECT username FROM users u WHERE u.id = %s;", (userID,))
	user = dict_cur.fetchone()[0]
	print "user: ", user, type(user)
	
	if user == None:
		flash('User %s not found.', (user))
		return redirect(url_for('login'))

	else:
		try:
			dict_cur.execute("SELECT * FROM sentences s WHERE s.id_user = %s;", (userID,))
			sentences = dict_cur.fetchall()
			print "\nsentences: "
			for record in sentences:
				print record, type(record)
		except Exception as e:
			print e

		return render_template('user.html',
								user=user,
								userID=userID,
								sentences=sentences
								)

@app.route("/input")
@login_required
def input_sentence():
	userID=request.args.get("userID")
	return render_template("input_sentence.html", 
							userID=userID)

@app.route("/sentence")
@login_required
def confirm_sentence():
	try:
		userID=request.args.get("userID")
		sentence=request.args.get("sentence").lower()
		language=request.args.get("language")
		date=request.args.get("date")
		paraphrase=request.args.get("paraphrase")
		sentence_type=request.args.get("sentence_type")
		sessionID=date+language
	except Exception as e:
		print e

		#strip out some punctuation
	punc = [".", ",", ";", "(", ")", "!", "\"", ":", "?"]
	for i in punc:
		sentence = sentence.replace(i, "")

	# print "sentence w/o punc: ", sentence

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
							userID=g.user.id))


@app.route('/delete_sent/<int:sent_id>')
@login_required
def delete_sent(sent_id):
	# sentence = Sentence.query.get(sent_id)
	dict_cur.execute("SELECT * FROM sentences WHERE id = %s;", (sent_id,))
	sentence = dict_cur.fetchone()
	# print "this is id", sent_id
	# print "this is sentence", sentence

	if sentence is None:
		flash('Sentence not found!')
		return redirect(url_for('user', 
								userID=g.user.id))
	# if userID != g.user.id:
	# 	flash('You cannot delete this sentence!')
	# 	return redirect(url_for('user', 
	# 							username=g.user.username))

	dict_cur.execute("DELETE FROM sentences WHERE sentences.id = %s;", (sent_id,))	
	return redirect(url_for('user', 
							userID=g.user.id))


@app.route("/tagPOS")
@login_required
def tag_pos():
	error= request.args.get("error")
	sentence = request.args.get("sentence")
	print sentence
	userID = request.args.get("userID")
	# language=request.args.get("sentence_language")
	
	dict_cur.execute("SELECT id from sentences WHERE sentence = %s;", (sentence,))
	sentenceID = dict_cur.fetchone()[0]
	print "sentenceID for tagPOS = ", sentenceID

	print "all done tag pos"
	return render_template("tag_words.html", 
							sentence=sentence, 
							userID=userID, 
							sentenceID=sentenceID, 
							error=error
							# language=language
							)

# @app.route("/confirmPOS")
# @login_required
# def pos_confirm():
# 	sentence=request.args.get("sentence")
# 	userID = request.args.get("userID")
# 	sentenceID = request.args.get("sentenceID")
# 	print "sentenceID for confirmPOS = ", sentenceID
# 	language = request.args.get("language")
# 	pos = ""
	
# 	for i in range(len(sentence.split())):
# 		if request.args.get(str(i)):
# 			try:
# 				pos=pos+(request.args.get(str(i)))+" "
# 			except Exception as e:
# 				print e
# 			print "pos: ", pos, type(pos)
# 		else:
# 			print "error"
# 			return redirect(url_for('tag_pos', 
# 									sentence=sentence, 
# 									userID=userID, 
# 									sentenceID=sentenceID, 
# 									error= 1, 
# 									language=language))
# 	print "done pos confirm"
# 	return render_template("POS_confirm.html", 
# 							sentence=sentence, 
# 							userID=userID, 
# 							sentenceID=sentenceID, 
# 							pos=pos, 
# 							language=language)

@app.route("/pos_to_db")
@login_required
def pos_to_db():
	print request.args
	redo = request.args.get("redo")
	print redo, "redo"
	userID = int(request.args.get("userID"))
	print "group userID:", userID, type(userID)
	sentenceID = int(request.args.get("sentenceID"))
	print "this is sentenceID", sentenceID
	sentence = str(request.args.get("sentence"))
	pos = ""
	print "pos: ", pos
	
	for i in range(len(sentence.split())):
		if request.args.get(str(i)):
			try:
				pos=pos+(request.args.get(str(i)))+" "
			except Exception as e:
				print e
			print "pos: ", pos, type(pos)
	
	if redo == None:
		# language=request.args.get("language") #this is not getting passed
		# print language, type(language)
		# pos_array = str(request.args.get("pos")).split()
		pos_array = pos.split()
		print pos_array, type(pos_array)
		words = sentence.split()
		print words, type(words)
		for i in range(len(words)):	
			try:
				#assign word_sentence_positions: check if already in wsp table, if not then add insert them
				word = words[i]
				print "\nword= ", word, type(word)
				print "wsp= ", i, type(i)

				dict_cur.execute("SELECT w.id, w.word, s.id, w.ws_linear_position FROM words w INNER JOIN sentences s ON w.id_sentence = s.id WHERE s.id = %s AND w.ws_linear_position = %s AND w.id_user = %s ORDER BY w.id ASC;", (sentenceID, i, userID))
				found_word = list(dict_cur.fetchall())

				if found_word != []: 
					print "found_word=", found_word, type(found_word)
					#delete words and their dependencies
					dict_cur.execute("DELETE FROM words w WHERE w.word = %s AND w.id_sentence = %s AND w.ws_linear_position = %s AND w.id_user = %s;", (word, sentenceID, i, userID))
					print "deleted word!"

				#insert record into words
				dict_cur.execute("INSERT INTO words (word, pos, ws_linear_position, id_sentence, id_user) VALUES (%s, %s, %s, %s, %s);", (words[i], pos_array[i], i, sentenceID, userID))
				print "sent word to db= ", words[i]
				
			except Exception as e:
				print e

			try:
				#delete existing entries for this sentence in phrases table
				dict_cur.execute("DELETE FROM phrases p WHERE p.id_user = %s AND p.id_sentence = %s;", (userID, sentenceID))
				print "deleted existing record in phrases table"

			except Exception as e:
				print e

		return redirect(url_for('group',
								userID=userID,
								sentenceID=sentenceID
								))


@app.route("/group/<userID>/<sentenceID>")
@login_required
def group(userID, sentenceID):
		dict_cur.execute("SELECT * FROM sentences s INNER JOIN users u ON s.id_user = u.id WHERE s.id = %s;", (sentenceID,))
		s_record = dict_cur.fetchone()
		sentence = str(s_record[3])
		print "group - sentence= ", sentence, type(sentence)	
		userID = int(userID)
		print "group - userID= ", userID, type(userID)
		sentenceID = int(sentenceID)
		print "group - sentenceID= ", sentenceID, type(sentenceID)

		#find existing records in phrases table for this sentence
		dict_cur.execute("SELECT * FROM phrases p WHERE p.id_sentence = %s;", (sentenceID,))
		identified_phrases = dict_cur.fetchall()
		if identified_phrases != []:
			identified_phrases = identified_phrases
		print identified_phrases, "identified_phrases"

		dict_cur.execute("SELECT w.id, w.word, w.ws_linear_position FROM words w INNER JOIN sentences s ON w.id_sentence=s.id WHERE s.id = %s AND w.id_user = %s;", (sentenceID, userID))
		wordlist = dict_cur.fetchall()
		print "group - wordlist: ", wordlist


		return render_template("group.html", 
				sentence=sentence, 
				userID=userID, 
				sentenceID=sentenceID,
				identified_phrases=identified_phrases,
				wordlist=wordlist)



@app.route("/confirm_phrase")
@login_required
def confirm_phrase():
	sentence = str(request.args.get("sentence"))
	print "tagps sentence: ", sentence, type(sentence)
	words = sentence.split()
	userID = int(request.args.get("userID"))
	sentenceID = int(request.args.get("sentenceID"))
	print "tag ps sentenceID: ", sentenceID
	phrase_type = str(request.args.get("phrase_type"))
	# phrase_structure=request.args.get("phrase_structure")
	# redo = request.args.get("redo")
	# print redo
	
	# if redo == "True":
	# 	print "redo true"
	# 	word_positions_in_phrase_string = request.args.get("word_positions_in_phrase")
	# else:

	words_in_phrase = str(request.args.get("words_in_phrase")).split("|")
	for word in words_in_phrase:
		if word == "":
			words_in_phrase.remove(word)

	wplist = []
	for word in words_in_phrase:
		word = ast.literal_eval(word)
		wplist.append(word)
		print word, type(word)

	print "words_in_phrase: ", wplist, type(wplist)
	
	phrase = ""
	for word in wplist:
		phrase = phrase + word[1] + " "

	phrase = phrase.rstrip()
	print phrase

	# " ".join([str(words[int(word_position)]) for word_position in word_positions_in_phrase])
	print "phrase: %s - %s" % (phrase, phrase_type)

	# phrase_type_dict = {"S":[("NP", "necessary"), ("VP", "necessary")], 
	# 					"NP": [("det","optional"), ("AP", "optional"), ("N","necessary"), ("PP","optional")], 
	# 					"VP":[("V","necessary"), ("PP","optional"), ("NP","optional"), ("NP2", "optional"), ("S","optional"), ("CP", "optional"), ("AP","optional"), ("PP2","optional")], 
	# 					"PP":[("P","necessary"), ("NP","optional") ,("PP","optional")], 
	# 					"AP":[("deg","optional"), ("A","necessary")], 
	# 					"CP": [("C","necessary"), ("S","necessary")] }

	# phrase_structure_options=phrase_type_dict[phrase_type]
	# print "PS options: ", phrase_structure_options
	return render_template("confirm_phrase.html", 
							sentence=sentence, 
							sentenceID=sentenceID,
							userID=userID, 
							phrase=phrase, 
							phrase_type=phrase_type, 
							# phrase_structure=phrase_structure, 
							words_in_phrase=wplist)


# @app.route("/confirm_phrase")
# @login_required
# def confirm_phrase():
# 	phrase_structure=request.args.get("phrase_structure")
# 	sentence= request.args.get("sentence")
# 	sentenceID=request.args.get("sentenceID")
# 	userID = request.args.get("userID")
# 	phrase_type = request.args.get("phrase_type")
# 	phrase=request.args.get("phrase")
# 	word_positions_in_phrase=request.args.get("word_positions_in_phrase")
# 	print word_positions_in_phrase, "word_positions_in_phrase"
# 	print phrase, "phrase"
# 	print phrase_structure, "phrase_structure"
# 	return render_template("confirm_phrase.html", 
# 							sentence=sentence, 
# 							userID=userID, 
# 							phrase=phrase, 
# 							phrase_type=phrase_type, 
# 							phrase_structure=phrase_structure, 
# 							sentenceID=sentenceID, 
# 							word_positions_in_phrase=word_positions_in_phrase)


@app.route("/phr_to_database")
@login_required
def put_phrase_in_database():
	print "prh in database"
	# phrase_structure = request.args.get("phrase_structure")
	# print "phrase structure: ", phrase_structure, type(phrase_structure)
	sentence = str(request.args.get("sentence"))
	sentenceID = int(request.args.get("sentenceID"))
	username=g.user.username
	phrase_type = str(request.args.get("phrase_type"))
	phrase = str(request.args.get("phrase"))
	print "phrase: ", phrase, type(phrase)
	words_in_phrase = ast.literal_eval(request.args.get("words_in_phrase"))
	print "words in phrase: ", words_in_phrase, type(words_in_phrase)
	userID = int(request.args.get("userID"))
	print "userID: ", userID, type(userID)

	try:
		#this gets the word id for the first word in the phrase
		firstwordid = words_in_phrase[0][0]
		print "firstwordid: ", firstwordid, type(firstwordid)
	except Exception as e:
		print e

	try:
		dict_cur.execute("SELECT * FROM phrases p INNER JOIN word_phrase_positions wpp ON p.id = wpp.id_phrase WHERE p.phrase = %s AND p.id_sentence = %s AND p.id_user = %s AND wpp.id_word = %s;", (phrase, sentenceID, userID, firstwordid))
		dup_phrase = list(dict_cur.fetchall())

		#delete duplicate phrase and its dependencies
		if dup_phrase != []:
			print "found duplicate phrase: ", dup_phrase, type(dup_phrase)
			for record in dup_phrase:
				dict_cur.execute("DELETE FROM phrases p WHERE p.id = %s;", (record[0],))
				print "deleted duplicate phrase entry: ", record
	except Exception as e:
		print e

	#insert phrase into phrases table
	try: 
		dict_cur.execute("INSERT INTO phrases (phrase, phrase_type, id_sentence, id_user) VALUES (%s, %s, %s, %s);", (phrase, phrase_type, sentenceID, userID))
	except Exception as e:
		print e
	print "inserted '%s' into phrases table" % (phrase)


	#get phrase ID
	try:
		dict_cur.execute("SELECT * FROM phrases p WHERE p.phrase = %s AND p.id_sentence = %s AND p.id_user = %s;", (phrase, sentenceID, userID))
		phraseID = dict_cur.fetchone()[0]
		print "phraseID: ", phraseID, type(phraseID)
	except Exception as e:
		print e

	#check word_phrase_positions table for existing duplicate entries
	try:
		for word in words_in_phrase:
			wordid = word[0]
			wordpos = words_in_phrase.index(word)
			dict_cur.execute("SELECT wpp.id, w.word, wpp.id_phrase FROM word_phrase_positions wpp INNER JOIN words w ON w.id = wpp.id_word INNER JOIN sentences s ON wpp.id_sentence = s.id WHERE wp_linear_position = %s AND wpp.id_word = %s AND wpp.id_phrase = %s AND s.id = %s AND s.id_user = %s;", (wordpos, wordid, phraseID, sentenceID, userID))
			found_wpp_match = list(dict_cur.fetchall())

			#delete wpp entries and their dependencies
			if found_wpp_match != []: 
				print "found_wpp_match=", found_wpp_match, type(found_wpp_match)
				dict_cur.execute("DELETE FROM word_phrase_positions wpp WHERE wp_linear_position = %s AND wpp.id_word = %s AND s.id = %s AND s.id_user = %s;", (wordpos, wordid, sentenceID, userID))
				print "deleted wpp entry!"

			#insert record into word_phrase_positions
			dict_cur.execute("INSERT INTO word_phrase_positions (wp_linear_position, id_word, id_sentence, id_phrase) VALUES (%s, %s, %s, %s);", (wordpos, wordid, sentenceID, phraseID))
			print "sent wpp to db= ", word[1]
	except Exception as e:
		print e

	#get linear position in sentence of first word in phrase
	try:
		dict_cur.execute("SELECT * FROM words w WHERE w.id = %s;", (firstwordid,))
		phrasefirstwordlinpos = dict_cur.fetchone()[3]
		print "phrasefirstwordlinpos: ", phrasefirstwordlinpos, type(phrasefirstwordlinpos)

	except Exception as e:
		print e

	#check phrase_sentence_positions table for existing duplicate entries
	try:
		dict_cur.execute("SELECT * FROM phrase_sentence_positions psp INNER JOIN phrases p ON psp.id_phrase = p.id WHERE psp.id_phrase = %s AND psp.id_sentence = %s AND p.id_user = %s;", (phraseID, sentenceID, userID))
		pspdup = dict_cur.fetchall()

		#delete duplicate entries in psp
		print "pspdup: ", pspdup, type(pspdup)		
		if pspdup != []:
			dict_cur.execute("DELETE FROM phrase_sentence_positions psp WHERE psp.ps_linear_position = %s AND psp.id_phrase = %s AND psp.id_sentence = %s;", (phrasefirstwordlinpos, phraseID, sentenceID))
			print "deleted from psp: ", phraseID

	except Exception as e:
		print e

	#insert into psp table
	try:
		dict_cur.execute("INSERT INTO phrase_sentence_positions (ps_linear_position, id_phrase, id_sentence) VALUES (%s, %s, %s);", (phrasefirstwordlinpos, phraseID, sentenceID))
		print "sent to phrase_sentence_positions: ", phraseID

	except Exception as e:
		print e

	return redirect(url_for('group', 
							redo=False, 
							sentence=sentence, 
							sentenceID=sentenceID, 
							userID=userID))

@app.route('/delete_phr/<int:phr_id>')
@login_required
def delete_phr(phr_id):
	userID = int(request.args.get("userID"))
	sentenceID = int(request.args.get("sentenceID"))
	dict_cur.execute("SELECT * FROM phrases WHERE id = %s;", (phr_id,))
	phrase = dict_cur.fetchone()
	# print "this is id", sent_id
	# print "this is sentence", sentence

	#this is copied from sentence delete - need to update it later 4/29/16
	if phrase is None:
		flash('Phrase not found!')
		return redirect(url_for('user', 
								username=g.user.username))
	# if userID != g.user.id:
	# 	flash('You cannot delete this sentence!')
	# 	return redirect(url_for('user', 
	# 							username=g.user.username))

	dict_cur.execute("DELETE FROM phrases p WHERE p.id = %s;", (phr_id,))	
	return redirect(url_for('group',
							userID=userID,
							sentenceID=sentenceID))

@app.route("/tagSubj")
@login_required
def tag_subj():
	error=request.args.get("error")
	sentence=request.args.get("sentence")
	sentenceID=request.args.get("sentenceID")
	userID = request.args.get("userID")
	phrases = []
	
	#get list of phrases for this sentence
	try:
		dict_cur.execute("SELECT id, phrase FROM phrases WHERE id_sentence = %s;", (sentenceID,))
		phrases= dict_cur.fetchall()
	except Exception as e:
		print e

	for phrase in phrases:
		print "id", phrase[0], "phrase: ", phrase[1]

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
	userID=int(request.args.get("userID"))
	sentence=str(request.args.get("sentence"))
	sentenceID=int(request.args.get("sentenceID"))
	subject=request.args.get("subject")
	try:
		subject_li=ast.literal_eval(subject)
		phraseID = subject_li[0]
		print type(subject_li), subject_li, "subject id: ", phraseID, type(phraseID)
	except Exception as e:
		print e
	print userID, type(userID)
	print sentence, type(sentence)
	print sentenceID, type(sentenceID)
	print type(subject), subject


	#this checks the gram_functions table for existing subjects for that sentence
	try:
		dict_cur.execute("SELECT * FROM gram_functions gf WHERE gf.gram_function = %s AND gf.id_sentence = %s;", (gramfunc, sentenceID))
		dup_sub = list(dict_cur.fetchall())

		if dup_sub != []:
			print "found duplicate subject: ", dup_sub, type(dup_sub)
			for record in dup_sub:
				dict_cur.execute("DELETE FROM gram_functions gf WHERE gf.id = %s;", (record[0],))
				print "deleted duplicate subject entry: ", record
	except Exception as e:
		print e

	#insert subject into gram_functions table
	try:
		dict_cur.execute("INSERT INTO gram_functions (gram_function, id_phrase, id_user, id_sentence) VALUES (%s, %s, %s, %s);", (gramfunc, phraseID, userID, sentenceID))
	except Exception as e:
		print e
	print "inserted into gram_functions table: ", gramfunc

	#get subject ID
	try:
		dict_cur.execute("SELECT * FROM gram_functions gf WHERE gf.id_phrase = %s AND gf.id_user = %s;", (phraseID, userID))
		subjectID = dict_cur.fetchone()[0]
		print "subjectID: ", subjectID
	except Exception as e:
		print e

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
		dict_cur.execute("SELECT id, phrase FROM phrases p WHERE p.id_sentence = %s AND p.id_user = %s;", (sentenceID, userID))
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
	try:
		dobject_li=ast.literal_eval(dobject)
		phraseID = dobject_li[0]
		print type(dobject_li), dobject_li, "direct object id: ", phraseID
	except Exception as e:
		print e
	print "userID: ", userID, type(userID)
	print "sentence: ", sentence, type(sentence)
	print "sentenceID: ", sentenceID, type(sentenceID)
	print type(dobject), dobject


	#this checks the gram_functions table for existing objects for that sentence
	try:
		dict_cur.execute("SELECT * FROM gram_functions gf WHERE gf.gram_function = %s AND gf.id_sentence = %s;", (gramfunc, sentenceID))
		dup_obj = list(dict_cur.fetchall())
		print "found duplicate direct object: ", dup_obj, type(dup_obj)

		if dup_obj != []:
			for record in dup_obj:
				dict_cur.execute("DELETE FROM gram_functions gf WHERE gf.id = %s;", (record[0],))
				print "deleted duplicate direct object entry: ", record
	except Exception as e:
		print e

	#insert direct object into gram_functions table
	try:
		dict_cur.execute("INSERT INTO gram_functions (gram_function, id_phrase, id_user, id_sentence) VALUES (%s, %s, %s, %s);", (gramfunc, phraseID, userID, sentenceID))
	except Exception as e:
		print e
	print "inserted into gram_functions table: ", gramfunc

	#get direct object ID
	try:
		dict_cur.execute("SELECT * FROM gram_functions gf WHERE gf.id_phrase = %s AND gf.id_user = %s;", (phraseID, userID))
		dobjID = dict_cur.fetchone()[0]
		print "dobjID: ", dobjID
	except Exception as e:
		print e

	return redirect(url_for('analyzed_sent',
							userID=userID,
							sentence=sentence,
							sentenceID=sentenceID
							))


# @app.route("/end")
# @login_required
# def prompt_new_sentence():
# 	DO=request.args.get("DO")
# 	IO=request.args.get("IO")
# 	wordIDs=request.args.get("wordIDString").split()
# 	if DO:
# 		for wordID in DO.split():
# 			try:
# 				dict_cur.execute("SELECT * from words_cases WHERE wordID ='{}' AND gram_case='ACC';".format(wordID))
# 				words_in_words_cases = dict_cur.fetchall()
# 			except Exception as e:
# 				print e
# 			print wordID
# 			print words_in_words_cases
# 			if words_in_words_cases == []:
# 				try:
# 					dict_cur.execute("INSERT INTO words_cases (wordID, gram_case) VALUES (%s, %s)", (wordID, "ACC"))
# 				except Exception as e:
# 					print e
# 			print wordID		
# 	if IO:
# 		for wordID in IO.split():
# 			try:
# 				dict_cur.execute("SELECT * FROM words_cases WHERE wordID ='{}' AND gram_case='DAT';".format(wordID))
# 				words_in_words_cases = dict_cur.fetchall()
# 			except Exception as e:
# 				print e
# 			print wordID
# 			print words_in_words_cases
# 			if words_in_words_cases == []:
# 				try:
# 					dict_cur.execute("INSERT INTO words_cases (wordID, gram_case) VALUES (%s, %s)", (wordID, "DAT"))
# 				except Exception as e:
# 					print e
# 			print wordID		

# 	return render_template("prompt_new_sentence.html")

@app.route("/analyzed_sent")
@login_required
def analyzed_sent():
	print "\nanalyzed_sent function"
	error= request.args.get("error")	
	userID = int(request.args.get("userID"))
	print "userID: ", userID
	sentence = str(request.args.get("sentence"))
	print "analyzed_sent: ", sentence, type(sentence)
	sentenceID = int(request.args.get("sentenceID"))
	print "sentenceID: ", sentenceID, type(sentenceID)


	try:
		#get sentence language
		dict_cur.execute("SELECT sentence_language sl FROM sentences s WHERE s.id=%s;", (sentenceID,))
		language = dict_cur.fetchone()[0].title()
		print "lang: ", language, type(language)

		#get list of parts of speech in sentence
		dict_cur.execute("SELECT word, pos FROM words w INNER JOIN sentences s ON w.id_sentence=s.id WHERE s.id=%s ORDER BY w.id ASC;", (sentenceID,))
		POSlist = dict_cur.fetchall()
		# for i in POSlist:
		# 	print i

		#get username for sentence
		dict_cur.execute("SELECT username FROM users WHERE id=%s;", (userID,))
		username = dict_cur.fetchone()[0]
		# print "username: ", username, type(username)

		#get sentene type for sentence
		dict_cur.execute("SELECT sentence_type FROM sentences WHERE id = %s;", (sentenceID,))
		sent_type = dict_cur.fetchone()[0]

		#get gloss for sentence
		dict_cur.execute("SELECT english_gloss FROM sentences WHERE id = %s;", (sentenceID,))
		english_gloss = dict_cur.fetchone()[0]

		#get notes for sentence
		dict_cur.execute("SELECT notes FROM sentences WHERE id = %s;", (sentenceID,))
		notes = dict_cur.fetchone()[0]

		#get collection date for sentence
		dict_cur.execute("SELECT collection_date FROM sentences WHERE id = %s;", (sentenceID,))
		collection_date = dict_cur.fetchone()[0].date()
		# print "collection date: ", collection_date, type(collection_date)


		dict_cur.execute("SELECT * FROM word_phrase_positions wpp INNER JOIN phrases p ON p.id=wpp.id_phrase WHERE p.id_sentence = %s AND wpp.wp_linear_position = 0 ORDER BY p.phrase_type ASC;", (sentenceID,))
		phrases = dict_cur.fetchall()
		print "phrases: ", phrases, type(phrases)

		#get distinct phrase types present in sentence
		dict_cur.execute("SELECT DISTINCT phrase_type FROM phrases p INNER JOIN sentences s ON p.id_sentence = s.id WHERE s.id = %s;", (sentenceID,))
		phrase_types = dict_cur.fetchall()

		ptlist = []
		for i in phrase_types:
			li = ast.literal_eval(str(i))
			print "li: ", li, type(li)
			ptlist.append(li)

		print "pt list: ", ptlist, type(ptlist)
		print "phrase types in sentence '%s' : %s" % (sentence, ptlist)

		phrase_groups = []
		for t in ptlist:
			print "type", t, type(t)
			print "t[0]: ", t[0], type(t[0])
			for p in phrases:
				print "p[7]: ", p[7], type(p[7])
				if p[7] == t[0]:
					t.append(p[6])
			phrase_groups.append(t)

		print "phrase groups: ", phrase_groups

		#get subject value
		try:
			gramfunc = "subject"
			dict_cur.execute("SELECT * FROM gram_functions gf INNER JOIN phrase_sentence_positions psp ON gf.id_phrase = psp.id_phrase INNER JOIN phrases p ON gf.id_phrase = p.id WHERE gf.id_user = %s AND gf.id_sentence = %s AND gf.gram_function = %s;", (userID, sentenceID, gramfunc))
			record = dict_cur.fetchone()
			subject = record[10]
			#get linear position of first word in subject
			subjectlinpos = record[6]
		except:
			subject = "no subject"
			subjectlinpos = "no subjectlinpos"
		
		print "subject: ", subject, type(subject)
		print "subjectlinpos: ", subjectlinpos, type(subjectlinpos)


		#get object value
		try:
			gramfunc = "direct object"
			dict_cur.execute("SELECT * FROM gram_functions gf INNER JOIN phrase_sentence_positions psp ON gf.id_phrase = psp.id_phrase INNER JOIN phrases p ON gf.id_phrase = p.id WHERE gf.id_user = %s AND gf.id_sentence = %s AND gf.gram_function = %s;", (userID, sentenceID, gramfunc))
			record = dict_cur.fetchone()
			dobj = record[10]

			#get linear position of first word in object
			dobjlinpos = record[6]
		except:
			dobj = "no object"
			dobjlinpos = "no dobjlinpos"

		print "dobj: ", dobj, type(dobj)
		print "dobjlinpos: ", dobjlinpos, type(dobjlinpos)


		#get verb value
		try:
			dict_cur.execute("SELECT * FROM words w WHERE w.id_sentence = %s AND w.id_user = %s AND w.pos = %s ORDER BY w.ws_linear_position ASC;", (sentenceID, userID, "verb"))
			records = dict_cur.fetchall()
			print "records: ", records
			
			if records == []:
				verb = "no verb"
				verbid = "no verbid"
				verblinpos = "no verblinpos"

			else:
				verblist = []
				for record in records:
					verb = record[1]
					verbid = record[0]
					verblinpos = record[5]
					print "verb record: ", record, type(record)
					verblist.append(record[1])
				
				verb = ""
				for i in verblist:
					verb = verb + " " + i
				verb = verb.strip()
				# print "verb: ", verb

				verblinpos = records[0][3]
				# print "verblinpos: ", verblinpos, type(verblinpos)

				verbid = records[0][0]
					#get linear position of verb
				# dict_cur.execute("SELECT * FROM words w WHERE w.id_sentence = %s AND w.id_user = %s AND w.id = %s;", (sentenceID, userID, verbid))
				# verblinpos = dict_cur.fetchone()[5]
		except Exception as e:
			print e

		print "verb: ", verb, type(verb)
		print "verbid: ", verbid, type(verbid)
		print "verblinpos: ", verblinpos, type(verblinpos)


		#determine basic word order based on above info
		if verb == "no verb" or subject == "no subject":
			bwo = []

		elif subjectlinpos < verblinpos and dobj == "no object":
			bwo = [["Subject", subject], ["Verb", verb], ["(SV)"]]

		elif subjectlinpos > verblinpos and dobj == "no object": 
			bwo = [["Verb", verb], ["Subject", subject], ["(VS)"]]

		elif verblinpos < subjectlinpos and subjectlinpos < dobjlinpos:
			bwo = [["Verb", verb], ["Subject", subject], ["Object", dobj], ["(VSO)"]]

		elif verblinpos > subjectlinpos and subjectlinpos > dobjlinpos:
			bwo = [["Object", dobj], ["Subject", subject], ["Verb", verb], ["(OSV)"]]

		elif verblinpos < dobjlinpos and dobjlinpos < subjectlinpos:
			bwo = [["Verb", verb], ["Object", dobj], ["Subject", subject], ["(VOS)"]]

		elif verblinpos > dobjlinpos and dobjlinpos > subjectlinpos:
			bwo = [["Subject", subject], ["Object", dobj], ["Verb", verb], ["(SOV)"]]

		elif subjectlinpos < verblinpos and verblinpos < dobjlinpos:
			bwo = [["Subject", subject], ["Verb", verb], ["Object", dobj], ["(SVO)"]]

		else: 
			bwo = [["Object", dobj], ["Verb", verb], ["Subject", subject], ["(OVS)"]]

		print "bwo: ", bwo, type(bwo)

	except Exception as e:
		print e

	#this is for the syntactic structure section of the analyzed sent page

	try:
		#create a list of words for the sentence
		dict_cur.execute("SELECT * FROM words w WHERE w.id_sentence = %s AND w.id_user = %s;", (sentenceID, userID))
		wrecords = dict_cur.fetchall()
		print "word_sent records: ", wrecords, type(wrecords)

		sent_word_list = []
		for record in wrecords:
			word = record[1]
			wordID = record[0]
			sent_word_list.append(wordID)
			# print "word and ID: ", word, wordID, type(word), type(wordID)

		print sent_word_list

		sent_phrase_list = []
		for wordID in sent_word_list:
			phrase_list = []
			dict_cur.execute("SELECT id_phrase FROM word_phrase_positions wpp WHERE wpp.id_sentence = %s AND wpp.id_word = %s;", (sentenceID, wordID))
			pwrecords = dict_cur.fetchall()

			for record in pwrecords:
				phrase_list.append(record[0])
			print "\nphrases containing wordID %s: %s" % (wordID, phrase_list) 

			sent_phrase_list.append(phrase_list)
		print "\nsent_phrase_list: %s" % (sent_phrase_list) 


		#create a phrase structure dictionary where the key:value pair is phrase ID: list of daughter phraseIDs 
		psdict = {}
		dict_cur.execute("SELECT * FROM phrases p WHERE p.id_sentence = %s AND p.id_user = %s;", (sentenceID, userID))
		precords = dict_cur.fetchall()

		#for each phrase in the dictionary, look at each other phrase and append it to the value list if it is a daughter
		for record in precords:
			const = []
			phraseID = record[0]
			print "phraseID: ", phraseID, type(phraseID)
			psdict[phraseID] = const


			for i in precords:
				#the and statement excludes the phraseID itself from the list
				if i[1] in record[1] and i[1] != record[1]:
					psdict[phraseID].append(i[0])

		print "psdict: ", psdict

		# for i in psdict:
		# 	mother = i
		# 	daughters = []

		# 	for i in psdict[i]:
		# 		daughters.append(i)

		# 	print mother, " = ", daughters[1:]

		#this will look at each mother (key), subtract the content of the daughters (value list), and append
		#what remains in the correct position in the list
		dict_cur.execute("SELECT * FROM word_phrase_positions wpp INNER JOIN words w ON wpp.id_word = w.id WHERE wpp.id_sentence = %s AND w.id_user = %s ORDER BY wpp.id_phrase, wpp.wp_linear_position;", (sentenceID, userID))
		wppwrecords = dict_cur.fetchall()

		# for record in wppwrecords:
		# 	print record, type(record)

		for key in psdict:
			#if the phrase key corresponds to an empty list, then add the pos for the phrase to the list
			if psdict[key] == []:
				for record in wppwrecords:
					if record[4] == key:
						psdict[key].append(record[7])

			else:
				#create dictionary made of a word list for each daughter in each mother
				dcontent = {}
				for value in psdict[key]:
					wordlist = []
					for record in wppwrecords:
						if record[4] == value:
							wordlist.append(record[2])
					dcontent[value] = wordlist 
				print "dcontent: ", key, dcontent

				#remove daughter content if it is subset of another daughter
				for i, a in dcontent.items():
					# print "i: ", i, a
					for j, b in dcontent.items():
						# print "j: ", j, b
						if i != j:
							if all(x in a for x in b):
								del dcontent[j]
				print "dcontent: ", key, dcontent

				#this updates psdict by removing phrases that are subsets of othe phrases
				dcontentlist = []
				for k in dcontent:
					dcontentlist.append(k)
				print "dcontentlist: ", dcontentlist
				psdict[key] = dcontentlist
				print "psdict: ", psdict

				#compare concatenated daughters to mother 
				#make a dict of words that are in the mother but not the daughter
				mother = []
				daughter = []
				remainderdict = {}				
				for item in dcontent:
					for item in dcontent[item]:
						daughter.append(item)
				print "daughter: ", key, daughter

				for record in wppwrecords:
					if record[4] == key:
						mother.append(record[2])
				print "mother: ", key, mother
				
				remainder = []		
				for i in mother:
					if i not in daughter:
						remainder.append(i)
					remainderdict[key] = remainder
				print "remainderdict: ", key, remainderdict

				# find POS and linear position in phrase for each remainder in remainderdict
				for remainder in remainderdict[key]:
					for record in wppwrecords:
						if record[2] == remainder and record[4] == key:
							remainderlinpos = record[1]
							remainderpos = record[7]
							print remainderlinpos, remainderpos

				#append remainder to value list in correct position relative to phrase daughters
				#as is, the appends the remainder first, rather than checking to see where it belongs
				#relative to other daughter phrases
				pscontent = [remainderpos]
				for value in psdict[key]:
					for record in precords:
						if value == record[0]:
							pscontent.append(record[2])
				print pscontent
				psdict[key] = pscontent

		print psdict
		for item in psdict:
			rule = ""
			for value in psdict[item]:
				rule = rule + " " + value
			print rule
			psdict[item] = rule.strip()
			
			#this checks the phrase structure rule table for duplicate entries
			try:
				dict_cur.execute("SELECT * FROM phrase_structure_rules psr WHERE psr.id_phrase = %s AND psr.id_sentence = %s;", (item, sentenceID))
				dup_psr = list(dict_cur.fetchall())

				if dup_psr != []:
					print "found duplicate psr: ", dup_psr, type(dup_psr)
					for record in dup_psr:
						dict_cur.execute("DELETE FROM phrase_structure_rules psr WHERE psr.id = %s;", (record[0],))
						print "deleted duplicate psr entry: ", record
			except Exception as e:
				print e

			#insert rule into psr table
			try:
				dict_cur.execute("INSERT INTO phrase_structure_rules (phrase_structure, id_phrase, id_user, id_sentence) VALUES (%s, %s, %s, %s);", (psdict[item], item, userID, sentenceID))
			except Exception as e:
				print e
			print "inserted into psr table: ", psdict[item]

		dict_cur.execute("SELECT * FROM phrase_structure_rules psr INNER JOIN phrases p ON psr.id_phrase = p.id WHERE psr.id_sentence = %s AND psr.id_user = %s ORDER BY p.phrase_type;", (sentenceID, userID))
		psr_records = dict_cur.fetchall()
		pslist = []
		for record in psr_records:
			mdlist = []
			mother = record[7]
			mdlist.append(mother)
			daughter = record[1]
			mdlist.append(daughter)
			# print "ps rule: ", psrule
			pslist.append(mdlist)
		for rule in pslist:
			print rule

		uniquepslist = []
		exists = set()
		for item in pslist:
			rule = item[0] + " = " + item[1]
			print rule
			if rule not in exists:
				uniquepslist.append(item)
				exists.add(rule)
		print "\nunique psr list:"
		for uniquerule in uniquepslist:
			print uniquerule


	except Exception as e:
				print e

	return render_template("analyzed_sent.html",
							username=userID,
							userID=userID,
							sentence=sentence,
							sentenceID=sentenceID,
							language=language,
							sent_type=sent_type,
							gloss=english_gloss,
							notes=notes, #there is no field to enter notes in the sentence input screen
							collection_date=collection_date,
							POSlist=POSlist,
							phrase_types=ptlist,
							phrase_groups=phrase_groups,
							phrases=phrases,
							bwo=bwo,
							uniquepslist=uniquepslist
							)

