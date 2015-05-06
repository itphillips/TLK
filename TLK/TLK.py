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

dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@app.route("/")
@app.route("/login")
def login():
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
		return redirect (url_for('signup', username=username, password=password))
	else:
		try:
			dict_cur.execute("SELECT * FROM sentences s INNER JOIN users_sentences us ON us.sentenceID=s.id WHERE us.userID='{0}'".format(userID[0]))
			sentences=dict_cur.fetchall()
		except Exception as e:
			print e
		return render_template("show_sentences.html", sentences=sentences, userID= userID[0])

@app.route("/signup", methods=["GET", "POST"])
def signup():
	username=request.args.get("username")
	password=request.args.get("password")

	if request.method=="GET":
		return render_template("signup.html", username=username, password=password)
	else:
		try:
			dict_cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",(username, password))
		except Exception as e:
			print e
		return redirect(url_for('show_sentences', username=username, password=password))


@app.route("/input")
def input_sentence():
	userID=request.args.get("userID")
	return render_template("input_sentence.html", userID=userID)

@app.route("/sentence")
def confirm_sentence():
	print "yoooo"
	try:
		userID=request.args.get("userID")
		sentence=request.args.get("sentence")
		language=request.args.get("language")
		date=request.args.get("date")
	except Exception as e:
		print e
	print userID
	print sentence
	print language
	print date
		#return redirect to same page with error message==make sure you fill in all fields.
	#continued_session=request.args.get("continued_session")

	return render_template("confirm_sentence.html", userID=userID, sentence=sentence, language=language, date=date)

@app.route("/tagPOS")
def tag_pos():
	error= request.args.get("error")
	sentence = request.args.get("sentence")
	userID = request.args.get("userID")
	language=request.args.get("language")

	if error:
		sentenceID= request.args.get("sentenceID")
		return render_template("tag_words2.html", sentence=sentence, userID=userID, sentenceID=sentenceID, error=error, language=language)

	try:
		date=request.args.get("date")
		sessionID=date+language
	except Exception as e:
		print e

	try:
		dict_cur.execute("SELECT sessionnumber FROM sentences s INNER JOIN users_sentences us ON us.userID=s.ID WHERE us.userID = '{}'  AND sessionID='{}';".format(userID, sessionID))
	except Exception as e:
		print e
	print dict_cur.fetchall()
	if dict_cur.fetchall() != []:
		sessionnumber=sessionnumber+1
	else:
		sessionnumber=1	
	print sessionnumber
	try:
		dict_cur.execute("INSERT INTO sentences (sentence, language, collection_date, sessionnumber, sessionID) VALUES (%s,%s, %s,%s, %s)",(sentence, language, date, sessionnumber, sessionID))
		dict_cur.execute("SELECT id FROM sentences WHERE sentence = '{}' AND collection_date = '{}' AND sessionID = '{}';".format (sentence, date, sessionID) )
		sentenceID= dict_cur.fetchone()[0]
		dict_cur.execute("INSERT INTO users_sentences (userID, sentenceID) VALUES (%s, %s)", (userID, sentenceID))
	except Exception as e:
		print e	

	return render_template("tag_words2.html", sentence=sentence, userID=userID, sentenceID=sentenceID, error=error, language=language)

@app.route("/confirmPOS")
def pos_confirm():
	sentence=request.args.get("sentence")
	userID = request.args.get("userID")
	sentenceID = request.args.get("sentenceID")
	pos = []
	for word in sentence.split():
		if request.args.get(word.lower()):
			try:
				pos.append(request.args.get(word.lower()))
			except Exception as e:
				print e
		else:
			return redirect(url_for('tag_pos', sentence=sentence, userID=userID, sentenceID=sentenceID, error= 1))
	sentencepos = collections.OrderedDict(zip(sentence.split(), pos))
	return render_template("POS_confirm.html", sentence=sentence, userID=userID, sentenceID=sentenceID, sentencepos=sentencepos)

@app.route("/group")
def group():
	language=request.args.get("language")
	userID = request.args.get("userID")
	sentenceID = request.args.get("sentenceID")
	sentence = request.args.get("sentence")
	for word in sentencepos.keys():
		try:
			pos = sentencepos[word]

			dict_cur.execute("SELECT id from words WHERE word = '{}' AND pos = '{}' AND language = '{}';".format(word, pos, language))

			if dict_cur.fetchall() == []:
				dict_cur.execute("INSERT INTO words (word, pos, language) VALUES (%s, %s, %s)", (word, pos, language))
				dict_cur.execute("SELECT id from words WHERE word = '{}' AND pos = '{}' AND language = '{}';".format(word, pos, language))

			wordID = dict_cur.fetchone()

			dict_cur.execute("INSERT INTO words_sentences (wordID, sentenceID) VALUES (%s, %s, %s)", (wordID, sentenceID))
		except Exception as e:
			print e

	return render_template("group.html")


if __name__ == '__main__':
    app.run()


