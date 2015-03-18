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

	query="SELECT id FROM users WHERE username = '{}' AND password= '{}';".format( username, password )
	dict_cur.execute(query)
	userID=dict_cur.fetchone()
	if userID == None:
		return redirect (url_for('signup', username=username, password=password))
		#return redirect (url_for('input_sentence'), username=username, password=password)
	else:
		try:
			dict_cur.execute("SELECT * FROM sentences s INNER JOIN users_sentences us ON us.sentenceID=s.id WHERE us.userID='{0}'".format(userID[0]))
			sentences=dict_cur.fetchall()
		except Exception as e:
			print e
		return render_template("show_sentences.html", sentences=sentences, username=username, password=password)

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
	username=request.args.get("username")
	password=request.args.get("password")
	print "hi"
	print username, password
	return render_template("input_sentence.html", username=username, password=password)

@app.route("/sentence")
def confirm_setence():

	username=request.args.get("username")
	password=request.args.get("password")
	sentence=request.args.get("sentence")
	language=request.args.get("language")
	date=request.args.get("date")
	#continued_session=request.args.get("continued_session")

	sessionID=date+language
	dict_cur.execute("SELECT sessionnumber FROM sentences WHERE username = '{0}' AND password = '{1}' AND sessionID='{2}';").format(username, password, sessionID)
	if dict_cur.fetchall != []:
		#may want to check if the sentence is identical or not...
		sessionnumber=sessionnumber+1
	else:
		sessionnumber=1	
	
	dict_cur.execute(dict_cur.execute("INSERT INTO sentences (username,password,sentence, language, collection_date, sessionnumber, sessionID) VALUES (%s,%s, %s,%s, %s, %s, %s)",(username,password,sentence, language, date, sessionnumber, sessionID)))

		

@app.route("/tagPOS")
def tag_pos(sentence="Susan and Ian are making an app"):
	return render_template("tag_words.html", sentence=sentence)

@app.route("/confirmPOS")
def pos_confirm():

	print "hi"
	try:
		sentence=request.args.get("sentence")
		print "got args"
		print sentence
	except Exception as e:
		print e
	return render_template("POS_confirm.html", sentence=sentence)

@app.route("/")
def pos_confirm_redirect():
	if request.args.get("YES!"):
		return render_template ("")
	else:
		return redirect(url_for("tag_pos")) 


if __name__ == '__main__':
    app.run()


