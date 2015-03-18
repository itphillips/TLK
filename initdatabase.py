import os
import psycopg2
import urlparse
from psycopg2 import extras
conn = psycopg2.connect("postgres://pmehzpfkeotntn:u4OXp20HhAef8TD8L9Hqk1LciC@ec2-174-129-21-42.compute-1.amazonaws.com:5432/d6ki3e1ckkv6f3")


dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()
cur.execute("CREATE TABLE sentences (id serial PRIMARY KEY, sessionID varchar, language varchar, collection_date date, sessionnumber int, notes varchar, collection_location varchar, sentence_type varchar, sentence varchar, eng_gloss varchar, correctness varchar );")
cur.execute("CREATE TABLE words (id serial PRIMARY KEY, word varchar, pos varchar, language varchar, gram_case varchar);")
cur.execute("CREATE TABLE words_sentences (id serial PRIMARY KEY, sentenceID int, wordID int);")
cur.execute("CREATE TABLE phrases (id serial PRIMARY KEY, phrase varchar, phrase_type varchar, wordtype1 varchar, wordtype2 varchar);") #there should be 15 of these!!
cur.execute("CREATE TABLE phrases_sentences (id serial PRIMARY KEY, sentenceID int, phraseID int);")
cur.execute("CREATE TABLE users (id serial PRIMARY KEY, username varchar, password varchar);")
cur.execute("CREATE TABLE users_sentences (id serial PRIMARY KEY, userID int, sentenceID int);")
conn.commit()


conn.close()