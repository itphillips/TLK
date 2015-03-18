from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import string
import psycopg2
import collections
import urlparse
from psycopg2 import extras


app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)

conn = psycopg2.connect("postgres://pmehzpfkeotntn:u4OXp20HhAef8TD8L9Hqk1LciC@ec2-174-129-21-42.compute-1.amazonaws.com:5432/d6ki3e1ckkv6f3")


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
		#this says it's working but secretly isn't (!)
		dict_cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",(username, password))
		return redirect(url_for('show_sentences', username=username, password=password))


@app.route("/input")
def input_sentence():
	userID=request.args.get("userID")
	return render_template("input_sentence.html", userID=userID)

@app.route("/sentence")
def confirm_sentence():
	userID=request.args.get("userID")
	sentence=request.args.get("sentence")
	language=request.args.get("language")
	date=request.args.get("date")

	#continued_session=request.args.get("continued_session")

	sessionID=date+language
	try:
		dict_cur.execute("SELECT sessionnumber FROM sentences s INNER JOIN users_sentences us ON us.userID=s.ID WHERE us.userID = '{}'  AND sessionID='{}';".format(userID, sessionID))
	except Exception as e:
		print e
	if dict_cur.fetchall() != []:
		#may want to check if the sentence is identical or not...
		sessionnumber=sessionnumber+1
	else:
		sessionnumber=1	
	
	try:
		dict_cur.execute("INSERT INTO sentences (sentence, language, collection_date, sessionnumber, sessionID) VALUES (%s,%s, %s,%s, %s)",(sentence, language, date, sessionnumber, sessionID))
		dict_cur.execute("SELECT id FROM sentences WHERE sentence = '{}' AND collection_date = '{}' AND sessionID = '{}';".format (sentence, date, sessionID) )
		sentenceID= dict_cur.fetchone()[0]
		dict_cur.execute("INSERT INTO users_sentences (userID, sentenceID) VALUES (%s, %s)", (userID, sentenceID))
	except Exception as e:
		print e	

	return render_template("confirm_sentence.html", sentence=sentence, sentenceID=sentenceID, userID=userID)
	#this template lets the user see if they like the sentence. If they don't, it redirects to input sentence. If they do, it directs to tag_pos

@app.route("/tagPOS")
def tag_pos():
	sentence = request.args.get(sentence)
	userID = request.args.get(userID)
	sentenceID = request.args.get(sentenceID)
	return render_template("tag_words.html", sentence=sentence, userID=userID, sentenceID=sentenceID)

@app.route("/confirmPOS")
def pos_confirm():
	sentence=request.args.get("sentence")
	userID = request.args.get(userID)
	sentenceID = request.args.get(sentenceID)
	return render_template("POS_confirm.html", sentence=sentence, userID=userID, sentenceID=sentenceID)

@app.route("/")
def pos_confirm_redirect():
	if request.args.get("YES!"):
		#THIS IS WHERE THIS STOPS WORKING!
		return render_template ("")
	else:
		return redirect(url_for("tag_pos")) 


if __name__ == '__main__':
    app.run()


