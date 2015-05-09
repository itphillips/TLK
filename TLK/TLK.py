from flask import Flask, request, redirect, url_for, render_template

import string
import psycopg2
import collections
import urlparse
import collections
from psycopg2 import extras


app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)

#conn = psycopg2.connect("postgres://pmehzpfkeotntn:u4OXp20HhAef8TD8L9Hqk1LciC@ec2-174-129-21-42.compute-1.amazonaws.com:5432/d6ki3e1ckkv6f3")
conn = psycopg2.connect("user=SusanSteinman") 
conn.set_session(autocommit=True)
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/login")
def login():
	dict_cur.execute("SELECT * FROM users;")
	print dict_cur.fetchall()
	dict_cur.execute("SELECT * FROM sentences;")
	print dict_cur.fetchall()
	dict_cur.execute("SELECT * FROM phrases;")
	print dict_cur.fetchall()
	dict_cur.execute("SELECT * FROM words;")
	print dict_cur.fetchall()
	try:
		dict_cur.execute("SELECT * FROM words_sentences;")
	except Exception as e:
		print e
	print dict_cur.fetchall()
	return render_template("login.html")

@app.route("/show_sentences")
def show_sentences():
	#this pulls any users from the database that match the credentials given. If there is one, it displays the sentences from this user.
	#if not, it 
	username=request.args.get("username")
	password=request.args.get("password")
	dict_cur.execute("SELECT id FROM users WHERE username = '{}' AND password= '{}';".format( username, password ))

	userID=dict_cur.fetchone()
	if userID == None:
		print "done show sentences"
		return redirect (url_for('signup', username=username, password=password))
	else:
		try:
			dict_cur.execute("SELECT * FROM sentences s INNER JOIN users_sentences us ON us.sentenceID=s.id WHERE us.userID='{0}'".format(userID[0]))
			sentences=dict_cur.fetchall()
		except Exception as e:
			print e
		print "done show sentences"
		return render_template("show_sentences.html", sentences=sentences, userID= userID[0])

@app.route("/signup", methods=["GET", "POST"])
def signup():
	username=request.args.get("username")
	password=request.args.get("password")

	if request.method=="GET":
		print "done signup"
		return render_template("signup.html", username=username, password=password)
	else:
		try:
			dict_cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",(username, password))
		except Exception as e:
			print e
		print "done signup"
		return redirect(url_for('show_sentences', username=username, password=password))


@app.route("/input")
def input_sentence():
	userID=request.args.get("userID")
	return render_template("input_sentence.html", userID=userID)

@app.route("/sentence")
def confirm_sentence():
	try:
		userID=request.args.get("userID")
		sentence=request.args.get("sentence")
		language=request.args.get("language")
		date=request.args.get("date")
	except Exception as e:
		print e
		#return redirect to same page with error message==make sure you fill in all fields.
	#continued_session=request.args.get("continued_session")
	print "done confirm_sentence"
	return render_template("confirm_sentence.html", userID=userID, sentence=sentence, language=language, date=date)

@app.route("/tagPOS")
def tag_pos():
	error= request.args.get("error")
	sentence = request.args.get("sentence")
	userID = request.args.get("userID")
	language=request.args.get("language")

	if error:
		sentenceID = request.args.get("sentenceID")
		return render_template("tag_words2.html", sentence=sentence, userID=userID, sentenceID=sentenceID, error=error, language=language)

	try:
		date=request.args.get("date")
		sessionID=date+language
	except Exception as e:
		print e
	print sessionID

	try:
		dict_cur.execute("SELECT sessionnumber FROM sentences s INNER JOIN users_sentences us ON us.userID=s.ID WHERE us.userID = '{}'  AND sessionID='{}';".format(userID, sessionID))
	except Exception as e:
		print e
	if dict_cur.fetchall() != []:
		sessionnumber=sessionnumber+1
	else:
		sessionnumber=1	
	try:
		#make sure that this sentence isn't already in the database
		dict_cur.execute("INSERT INTO sentences (sentence, language, collection_date, sessionnumber, sessionID) VALUES (%s,%s, %s,%s, %s)",(sentence, language, date, sessionnumber, sessionID))
		dict_cur.execute("SELECT id FROM sentences WHERE sentence = '{}' AND collection_date = '{}' AND sessionID = '{}';".format (sentence, date, sessionID) )
		sentenceID= dict_cur.fetchone()[0]
		#make sure that this sentence isn't already in the database users-sentennces
		dict_cur.execute("INSERT INTO users_sentences (userID, sentenceID) VALUES (%s, %s)", (userID, sentenceID))
	except Exception as e:
		print e	
	print "all done tag pos"
	return render_template("tag_words2.html", sentence=sentence, userID=userID, sentenceID=sentenceID, error=error, language=language)

@app.route("/confirmPOS")
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
			return redirect(url_for('tag_pos', sentence=sentence, userID=userID, sentenceID=sentenceID, error= 1, language=language))
	print "done pos confirm"
	return render_template("POS_confirm.html", sentence=sentence, userID=userID, sentenceID=sentenceID, pos=pos, language=language)

@app.route("/group")
def group():
	print request.args
	redo = request.args.get("redo")
	print redo, "redo"
	userID = request.args.get("userID")
	sentenceID = request.args.get("sentenceID")
	sentence = request.args.get("sentence")

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
					dict_cur.execute("INSERT INTO words (word, pos, language) VALUES (%s, %s, %s)", (words[i], pos_array[i], language))
					dict_cur.execute("SELECT id from words WHERE word = '{}' AND pos = '{}' AND language = '{}';".format(words[i], pos_array[i], language))
					found_words = dict_cur.fetchall()
				wordID = found_words[0]["id"]
				dict_cur.execute("SELECT id from words_sentences WHERE wordID = '{}' AND sentenceID = '{}';".format(wordID, sentenceID))
				found_words_sentences=dict_cur.fetchall()
				if found_words_sentences == []:
					dict_cur.execute("INSERT INTO words_sentences (wordID, sentenceID, position) VALUES (%s, %s, %s)", (wordID, sentenceID, i))
			except Exception as e:
				print e

	print "hallo"
	return render_template("group.html", sentence=sentence, userID=userID, sentenceID=sentenceID)

@app.route("/tag_phr_struct")
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
		dict_cur.execute("INSERT INTO phrases (phrase, phrase_type, phrase_subtype) VALUES (%s, %s, %s)", (phrase, phrase_type, phrase_structure))
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
	#anddd check to see if they're in words_[hrases. They probably are if they're in one of the others...need to reason about this]
	for i in range(len(word_ids_in_phrase)):
		try:
			dict_cur.execute("INSERT INTO words_phrases (wordID, phraseID, position) VALUES (%s, %s, %s)", (wordIDs[i], phraseID, i))
		except Exception as e:
			print e
	print "hi"
	return redirect(url_for('group', redo=False, sentence=sentence, sentenceID=sentenceID, userID=userID))

@app.route("/tagSubj")
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
def confirm_subj():
	sentence=request.args.get("sentence")
	wordIDString=request.args.get(wordIDString)
	word_IDs_of_subject_string=request.args.get("subject")
	word_IDs_of_subject_list=request.args.get("subject").split()

	return render_template("confirm_subj.html")

@app.route("/tag_obj")
def tag_obj():
	sentence=request.args.get("sentence")
	print sentence
	wordIDString=request.args.get("wordIDString")
	print wordIDString
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

@app.route("/end")
def save_obj_prompt_new_sentence():
	DOIOstring=request.args.get("object")
	DOIOlist=DOIOstring.replace("DO","").split("IO")
	DO=DOIOlist[0]
	IO=DOIOlist[1]
	if DO != "_":
		DO.replace("_","")
	else:
		DO=None
	if IO != "_":
		IO.replace("_","")
	else:
		IO=None

	return render_template("confirm_obj.html")

if __name__ == '__main__':
    app.run()


