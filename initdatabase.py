import os
import psycopg2
import urlparse
from psycopg2 import extras
#conn = psycopg2.connect("postgres://pmehzpfkeotntn:u4OXp20HhAef8TD8L9Hqk1LciC@ec2-174-129-21-42.compute-1.amazonaws.com:5432/d6ki3e1ckkv6f3")
conn = psycopg2.connect("user=SusanSteinman")

dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()
try:
	#cur.execute("CREATE TABLE sentences (id serial PRIMARY KEY, sessionID varchar, language varchar, collection_date date, sessionnumber int, notes varchar, collection_location varchar, sentence_type varchar, sentence varchar, eng_gloss varchar, correctness varchar );")
	#cur.execute("CREATE TABLE words (id serial PRIMARY KEY, word varchar, pos varchar, language varchar, gram_case varchar);")
	#cur.execute("CREATE TABLE words_sentences (id serial PRIMARY KEY, sentenceID int, wordID int, position int);")
	#cur.execute("CREATE TABLE phrases (id serial PRIMARY KEY, phrase varchar, phrase_type varchar, phrase_subtype varchar);")
	#cur.execute("CREATE TABLE phrases_sentences (id serial PRIMARY KEY, sentenceID int, phraseID int);")
	#cur.execute("CREATE TABLE words_phrases (id serial PRIMARY KEY, wordID int, phraseID int, position int);")
	#cur.execute("CREATE TABLE users (id serial PRIMARY KEY, username varchar, password varchar);")
	#cur.execute("CREATE TABLE users_sentences (id serial PRIMARY KEY, userID int, sentenceID int);")
	cur.execute("CREATE TABLE words_cases (id serial PRIMARY KEY, wordID int, gram_case varchar);")
	conn.commit()

except Exception as e:
	print e

conn.close()