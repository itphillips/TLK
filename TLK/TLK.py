from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import string
import psycopg2
import collections
import urlparse
from psycopg2 import extras


app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)



@app.route("/")
def login():
	return render_template("login.html")

@app.route("/<username>")
def show_sentences():
	#this pulls any users from the database that match the credentials given. If there is one, it displays the sentences from this user.
	#if not, it 
	pass

def input_sentence():
	pass


@app.route("/tag")
def tag_pos(sentence="Susan and Ian are making an app"):
	words=sentence.split()
	return render_template("tag_words.html", words=words)

@app.route("/confirmPOS")
@app.route("/tag/<word>")
def pos_confirm(words):
	print "hi"
	for word in words:
		print request.args.get("word")
	return render_template("login.html")
if __name__ == '__main__':
    app.run()


