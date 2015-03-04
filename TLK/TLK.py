from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import string
import psycopg2
import urlparse
from psycopg2 import extras


app = Flask(__name__)
app.config.from_object(__name__)

if __name__ == '__main__':
    app.run()
