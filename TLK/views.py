
from TLK import app
from flask import render_template, url_for, request, redirect, jsonify

print "hi!"
@app.route("/start")
def start():
	return render_template("test.html")