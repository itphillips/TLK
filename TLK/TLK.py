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
def login():
	return render_template("login.html")

@app.route("/show_sentences")
def show_sentences():
	#this pulls any users from the database that match the credentials given. If there is one, it displays the sentences from this user.
	#if not, it 
	username=request.args.get("username")
	print username, "username"
	dict_cur.execute("SELECT * FROM sentences WHERE username = '{0}';".format( username ))
	sentences=dict_cur.fetchall()
	if sentences == []:
		return redirect (url_for('input_sentence'))

def input_sentence():
	pass


@app.route("/tag")
def tag_pos(sentence="Susan and Ian are making an app"):
	words=sentence.split()
	return render_template("tag_words.html", words=words)

@app.route("/confirmPOS")
def pos_confirm():
	words=request.args.get("words")
	print words
	return render_template("tag_words.html", words=words)

if __name__ == '__main__':
    app.run()


