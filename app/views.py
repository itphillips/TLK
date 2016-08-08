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


#imports the app variable from the app package
from app import app, db, lm, oid 
from flask import Flask, render_template, url_for, request, redirect, jsonify, flash, session, g
from datetime import datetime
import string
import psycopg2
import collections
import urlparse
import ast
from psycopg2 import extras
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import LoginForm
from .models import User, Sentence, Word, Phrase, Word_phrase_position, Phrase_sentence_position, Gram_function, Phrase_structure_rule

conn = psycopg2.connect('postgresql://ianphillips@localhost/tlk')
conn.set_session(autocommit=True)
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@lm.user_loader
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

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler 
def login():
	print "\nthis is login:"
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('user', userID=g.user.id))

	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data 
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])

	return render_template('login.html',
							form=form,
							providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
	print "\nthis is after_login:"

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
	print "\nthis is logout:"

	logout_user()
	return redirect(url_for('home'))


@app.route('/user/<userID>')
@login_required 
def user(userID): #'userID' gets passed from after_login(), =g.user.id
	print "\nthis is user:"

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
			dict_cur.execute("SELECT * FROM sentences s WHERE s.id_user = %s ORDER BY s.id DESC;", (userID,))
			sentences = dict_cur.fetchall()
			print "\nsentences: "
			for record in sentences:
				print record, type(record), "\n"
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
	print "\nthis is input_sentence:"

	userID=request.args.get("userID")
	return render_template("input_sentence.html", 
							userID=userID)

@app.route("/sentence")
@login_required
def confirm_sentence():
	print "\nthis is confirm_sentence:"

	try:
		userID=request.args.get("userID")
		sentence=request.args.get("sentence").lower()
		language=request.args.get("language")
		paraphrase=request.args.get("paraphrase")
		sentence_type=request.args.get("sentence_type")
		notes=request.args.get("notes")
		date_added = datetime.utcnow()
	except Exception as e:
		print e

		#strip out some punctuation
	punc = [".", ",", ";", "(", ")", "!", "\"", ":", "?"]
	for i in punc:
		sentence = sentence.replace(i, "")

	try:
		#make sure that this sentence isn't already in the database
		dict_cur.execute("INSERT INTO sentences (sentence, sentence_language, english_gloss, id_user, sentence_type, notes, date_added) VALUES (%s, %s, %s, %s, %s, %s, %s)",(sentence, language, paraphrase, userID, sentence_type, notes, date_added))
	except Exception as e:
		print e

	print "done confirm_sentence"
	return redirect(url_for('user',
							userID=g.user.id))


@app.route('/delete_sent/<int:sent_id>')
@login_required
def delete_sent(sent_id):
	print "\nthis is delete_sent:"

	dict_cur.execute("SELECT * FROM sentences WHERE id = %s;", (sent_id,))
	sentence = dict_cur.fetchone()

	if sentence is None:
		flash('Sentence not found!')
		return redirect(url_for('user', 
								userID=g.user.id))

	dict_cur.execute("DELETE FROM sentences WHERE sentences.id = %s;", (sent_id,))	
	return redirect(url_for('user', 
							userID=g.user.id))


@app.route("/tagPOS")
@login_required
def tag_pos():
	print "\nthis is tag_pos:"

	error= request.args.get("error")
	sentence = request.args.get("sentence")
	print sentence
	userID = request.args.get("userID")
	
	dict_cur.execute("SELECT id from sentences WHERE sentence = %s;", (sentence,))
	sentenceID = dict_cur.fetchone()[0]
	print "sentenceID for tagPOS = ", sentenceID

	print "all done tag pos"
	return render_template("tag_words.html", 
							sentence=sentence, 
							userID=userID, 
							sentenceID=sentenceID, 
							error=error
							)


@app.route("/pos_to_db")
@login_required
def pos_to_db():
	print "\nthis is pos_to_db"

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
	print "\nthis is group:"

	dict_cur.execute("SELECT * FROM sentences s INNER JOIN users u ON s.id_user = u.id WHERE s.id = %s;", (sentenceID,))
	s_record = dict_cur.fetchone()
	sentence = str(s_record[1])
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
	print "\nthis is confirm_phrase:"

	sentence = str(request.args.get("sentence"))
	print "tagps sentence: ", sentence, type(sentence)
	words = sentence.split()
	userID = int(request.args.get("userID"))
	sentenceID = int(request.args.get("sentenceID"))
	print "tag ps sentenceID: ", sentenceID
	phrase_type = str(request.args.get("phrase_type"))

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

	print "phrase: %s - %s" % (phrase, phrase_type)

	return render_template("confirm_phrase.html", 
							sentence=sentence, 
							sentenceID=sentenceID,
							userID=userID, 
							phrase=phrase, 
							phrase_type=phrase_type, 
							words_in_phrase=wplist)



@app.route("/phr_to_database")
@login_required
def put_phrase_in_database():
	print "\n this is put_phrase_in_database:"
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
	print "\nthis is delete_phr:"

	userID = int(request.args.get("userID"))
	sentenceID = int(request.args.get("sentenceID"))
	dict_cur.execute("SELECT * FROM phrases WHERE id = %s;", (phr_id,))
	phrase = dict_cur.fetchone()

	if phrase is None:
		flash('Phrase not found!')
		return redirect(url_for('user', 
								username=g.user.username))


	dict_cur.execute("DELETE FROM phrases p WHERE p.id = %s;", (phr_id,))	
	return redirect(url_for('group',
							userID=userID,
							sentenceID=sentenceID))


@app.route("/tagSubj")
@login_required
def tag_subj():
	print "\nthis is tag_subj:"

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
	print "\nthis is confirm_subj:"

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
	print "\nthis is tag_obj:"

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
	print "\nthis is confirm_obj:"

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



@app.route("/analyzed_sent")
@login_required
def analyzed_sent():
	print "\nthis is analyzed_sent:"

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

		dict_cur.execute("SELECT * FROM word_phrase_positions wpp INNER JOIN phrases p ON p.id=wpp.id_phrase WHERE p.id_sentence = %s AND wpp.wp_linear_position = 0 ORDER BY p.phrase_type ASC;", (sentenceID,))
		phrases = dict_cur.fetchall()
		print "\nphrases: ", phrases, type(phrases)

		# get distinct phrase types present in sentence
		dict_cur.execute("SELECT DISTINCT phrase_type FROM phrases p INNER JOIN sentences s ON p.id_sentence = s.id WHERE s.id = %s;", (sentenceID,))
		phrase_types = dict_cur.fetchall()

		ptlist = []
		for i in phrase_types:
			li = ast.literal_eval(str(i))
			print "li: ", li, type(li)
			ptlist.append(li)

		print "\npt list: ", ptlist, type(ptlist)

		# create a list of items where each item is a list consisting of a unique phrase type
		# present in the sentence and the content of the phrases that are of that type
		phrase_groups = []
		for t in ptlist:
			print "type", t, type(t)
			print "t[0]: ", t[0], type(t[0])
			for p in phrases:
				if p[7] == t[0]:
					t.append(p[6])
			phrase_groups.append(t)

		print "phrase groups: ", phrase_groups

	except Exception as e:
		print e

	# get subject value
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
		
	print "\nsubject: ", subject, type(subject)
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

	print "\ndobj: ", dobj, type(dobj)
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
	except Exception as e:
		print e

	print "verb: ", verb, type(verb)
	print "verbid: ", verbid, type(verbid)
	print "verblinpos: ", verblinpos, type(verblinpos)


	#determine basic word order based on above info
	try:
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

	#this generates the syntactic structure section of the analyzed sent page
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

	except Exception as e:
		print e


	try:
		#create a phrase structure dictionary where the key:value pair is phrase ID: list of daughter phraseIDs 
		psdict = {}
		dict_cur.execute("SELECT * FROM phrases p INNER JOIN phrase_sentence_positions psp ON p.id=psp.id_phrase WHERE p.id_sentence = %s AND p.id_user = %s;", (sentenceID, userID))
		precords = dict_cur.fetchall()

		#for each phrase in the dictionary, look at each other phrase and append it to the value list if it is a daughter
		for record in precords:
			print "\nprecord: ", record, type(record)
			const = []
			phraseID = record[0]
			print "phraseID: ", phraseID, type(phraseID)
			psdict[phraseID] = const


			for i in precords:
				#need these variables to make i equal to one or more words
				#without this, the phrase corresponding to the pronoun "i"
				#will get added to const for any phrase containing the just letter "i"
				imidsent = " " + i[1] + " "
				isentonset = i[1] + " "
				isentoffset = " " + i[1]

				#the and statement excludes the phraseID itself from the list
				if imidsent in record[1] and i[1] != record[1]:
					psdict[phraseID].append(i[0])

				elif isentonset in record[1] and i[1] != record[1]:
					psdict[phraseID].append(i[0])

				elif isentoffset in record[1] and i[1] != record[1]:
					psdict[phraseID].append(i[0])

		print "\npsdict: ", psdict

	except Exception as e:
		print e

	uniquepslist = []
	try:
		#each phrase that is identified as a daughter of something will get added to this list; the point is that
		#whatever phrases don't get added here will be the top level phrases that go into the sentence
		#PS rule (e.g., S = NP VP)
		listofalldaughters = []

		#this will look at each mother (key), subtract the content of the daughters (value list), and append
		#what remains in the correct position in the list
		dict_cur.execute("SELECT * FROM word_phrase_positions wpp INNER JOIN words w ON wpp.id_word = w.id WHERE wpp.id_sentence = %s AND w.id_user = %s ORDER BY wpp.id_phrase, wpp.wp_linear_position;", (sentenceID, userID))
		wppwrecords = dict_cur.fetchall()

		for record in wppwrecords:
			print record, type(record)

		for key in psdict:
			#if the phrase key corresponds to an empty list, then add the pos for the phrase to the list
			if psdict[key] == []:
				for record in wppwrecords:
					if record[4] == key:
						psdict[key].append(record[7])

			else:
				#create dictionary made of a word list for each daughter in each mother
				dcontent = {}
				pruledict = {} #this is where daughter phrases and remainders will go as linpos:p-type or pos
				for value in psdict[key]:
					wordlist = []
					for record in wppwrecords:
						if record[4] == value:
							wordlist.append(record[2])
					dcontent[value] = wordlist 
				print "\ndcontent (all daughter phrases w/ words): ", key, dcontent

				#remove daughter content if it is subset of another daughter
				for i, a in dcontent.items():
					# print "i: ", i, a
					for j, b in dcontent.items():
						# print "j: ", j, b
						if i != j:
							if all(x in a for x in b):
								del dcontent[j]
				print "dcontent (subsets removed): ", key, dcontent

				#this updates psdict by removing phrases that are daughters of daughter phrases
				dcontentlist = []
				for k in dcontent:
					dcontentlist.append(k)
				print "dcontentlist: ", dcontentlist
				for i in dcontentlist:
					listofalldaughters.append(i)

				psdict[key] = dcontentlist
				print "psdict: ", psdict

				#for each item in dcontentlist, this adds to pruledict the linpos:p-type as a key:value pair
				for i in dcontentlist:
					for record in precords:
						if i == record[0]:
							pruledict[record[6]] = record[2]

				print "pruledict: ", pruledict

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
				pscontent = []
				for remainder in remainderdict[key]:
					for record in wppwrecords:
						if record[2] == remainder and record[4] == key:
							remainderlinpos = record[8]
							remainderpos = record[7]
							print "remainderlinpos & remainderpos: ", remainderlinpos, remainderpos

							#add remainderlinpos:remainderpos to pruledict as key:value pair
							pruledict[remainderlinpos] = remainderpos

				print "pruledict entries for key: ", key, pruledict

				#create a list from the pruledict, where the order of items is determined by the key value
				#this will create a list that is made of remainderpos and p-types in the right linear order
				sentlen = len(wrecords)

				for i in range(sentlen):
					if i in pruledict.keys():
						pscontent.append(pruledict[i])


				print "pscontent: ", pscontent
				psdict[key] = pscontent

		print "\nlistofalldaughters: ", listofalldaughters
		print "\npruledict: ", pruledict
		print "\npsdict: ", psdict

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
					print "\nfound duplicate psr: ", dup_psr, type(dup_psr)
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
			print "\ninserted into psr table: ", psdict[item]

		dict_cur.execute("SELECT * FROM phrase_structure_rules psr INNER JOIN phrases p ON psr.id_phrase = p.id WHERE psr.id_sentence = %s AND psr.id_user = %s ORDER BY p.phrase_type;", (sentenceID, userID))
		psr_records = dict_cur.fetchall()
		pslist = []
		for record in psr_records:
			mdlist = []
			mother = record[7]
			mdlist.append(mother)
			daughter = record[1]
			mdlist.append(daughter)
			pslist.append(mdlist)
		for rule in pslist:
			print rule


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

	try:
		#this will created the ps rule for the sentence
		dict_cur.execute("SELECT * from phrase_sentence_positions psp INNER JOIN phrases p ON psp.id_phrase = p.id WHERE psp.id_sentence = %s ORDER BY ps_linear_position ASC;", (sentenceID,))
		psp_records = dict_cur.fetchall()
		sent_top_phrases = []
		print "psp_records: ", psp_records
		
		for i in psp_records:
			if i[2] not in listofalldaughters:
				sent_top_phrases.append(i[6])
		print "sent_top_phrases: ", sent_top_phrases

		ps_rule = ""
		for i in sent_top_phrases:
			ps_rule = ps_rule + " " + i

		sent_ps_rule = ps_rule.strip()
		print "sent_ps_rule: ", sent_ps_rule

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
							notes=notes,
							POSlist=POSlist,
							phrase_types=ptlist,
							phrase_groups=phrase_groups,
							phrases=phrases,
							bwo=bwo,
							uniquepslist=uniquepslist,
							sent_ps_rule=sent_ps_rule
							)

