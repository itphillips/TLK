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
		sentenceID = request.args.get("sentenceID")
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
		print word
		if request.args.get(word.lower()):
			print request.args.get(word.lower())
			try:
				pos.append(request.args.get(word.lower()))
			except Exception as e:
				print e
		else:
			return redirect(url_for('tag_pos', sentence=sentence, userID=userID, sentenceID=sentenceID, error= 1))
	print  "all done"
	return render_template("POS_confirm.html", sentence=sentence, userID=userID, sentenceID=sentenceID, pos=pos)

@app.route("/group")
def group():
	language=request.args.get("language")
	userID = request.args.get("userID")
	sentenceID = request.args.get("sentenceID")
	sentence = request.args.get("sentence")
	pos = request.args.get("pos")
	words = sentence.split()
	print pos
	for i in range(len(words)):
		print words[i]
		try:
			dict_cur.execute("SELECT id from words WHERE word = '{}' AND pos = '{}' AND language = '{}';".format(words[i], pos[i], language))

			if dict_cur.fetchall() == []:
				dict_cur.execute("INSERT INTO words (word, pos, language) VALUES (%s, %s, %s)", (words[i], pos[i], language))
				dict_cur.execute("SELECT id from words WHERE word = '{}' AND pos = '{}' AND language = '{}';".format(words[i], pos[i], language))

			wordID = dict_cur.fetchone()

			dict_cur.execute("INSERT INTO words_sentences (wordID, sentenceID) VALUES (%s, %s, %s)", (wordID, sentenceID))
		except Exception as e:
			print e

	return render_template("group.html", sentence=sentence, userID=userID)

@app.route("/record")
def record_phrase():
	sentence= request.args.get("sentence")
	userID = request.args.get("userID")
	return redirect(url_for("group"), sentence=sentence, userID= userID)

if __name__ == '__main__':
    app.run()


