#****************************LEVEL 1***************************

#this contains the functions needed to collect and store TLK level 1 metadata

import string
import psycopg2
import urlparse
from psycopg2 import extras

#connect to psql database
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse("")
conn = psycopg2.connect(
database=url.path[1:],
user=url.username,
password=url.password,
host=url.hostname,
port=url.port
)
conn.set_session(autocommit=True)
dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

input_sent = raw_input("Please enter one sentence with all punctuation: ")
#This function asks the user to input a sentence
def get_sent():
    a = input_sent 
    return a

#This function splits the sentence into individual words; replaces punctuation with a space
#This function needs to be revised so that contractions get split in the right place
#before "n't", not at "'"

#this converts caps to lowercase
def sent_cleanup(whole_sent):
    words = string.lower(whole_sent)

#This loop goes through all of these characters and if that character is in the main file, 
#it replaces it with a space (for easier splitting)
    for punct in ["!", '"', ":", "\n", ";", ".", ",", "?", "$", "(", ")", "-"]:
        words = string.replace(words, punct, " ")
    	b = string.split(words, " ")
    return b

#this function creates a dictionary called "sentence_dict"
def tag_pos(word_lists):
    sentence_dict = {}
    
#This loop goes through all of the words in the input and asks what the part-of-speech tag
#should be, then adds this value-key pair to the dictionary "sentence_dict"
    for word in word_lists:
        print "What part of speech does '" + word + "' belong to?"
        b = raw_input(" ")
        sentence_dict.update({word:b})
    return sentence_dict

#this function checks the info that the user has entered; it re-runs tag_pos() if the info
#is incorrect; it asks for a new sentence if the info is correct
def pos_confirm(pos_tags):
    print pos_tags
    
    confirmation = raw_input("Is this information correct?")
    
    if confirmation == "0":
        levonemain()
    else:
        for word in pos_tags:
            # check to see if word, pos, language are in the database. If they are don't put them in again. Can I do this without repetition? 
            # ALSO! Make all the caps lower.
            dict_cur.execute("SELECT id FROM words WHERE word='{0}' AND pos= '{1}' AND language='{2}');".format(word, pos_tags[word], "english"))
            wordID = int(dict_cur.fetchone())
            if not wordID:
                dict_cur.execute("INSERT INTO words(word, pos, language) VALUES (%s,%s, %s)",(word, pos_tags[word],"english"))
                dict_cur.execute("SELECT id FROM words WHERE word='{0}' AND pos= '{1}' AND language='{2}');".format(word, pos_tags[word], "english"))
                wordID = int(dict_cur.fetchone())
            #dict_cur.execute("INSERT INTO words_sentences(sentenceID, wordID) VALUES (%i, %i)", (sentenceID, wordID)
        print "Great! Let's continue."


#this function runs all of the small functions (above) that are needed to gather TLK
#Level 1 (part-of-speech) data
def levonemain():
#this variable is the whole sentence that the user inputs
    whole_sent = get_sent()
#this variable is the output of sent_cleanup when performed on whole_sent
    split_sent = sent_cleanup(whole_sent)
#this variable is the output of tag_pos when performed on split_sent
    pos_tags = tag_pos(split_sent)
	
    pos_confirm(pos_tags)


#this calls the main Level 1 function: starts with a whole sentence input by the user
#and ends by adding each word and its part-of-speech tag to the dictionary sentence_dict
levonemain()

#****************** LEVEL 2 *********************************************************

#this contains the functions needed to collect and store TLK level 2 data

print "Now we're going to identify the syntactic constituents in the sentence."
print "Here is the sentence you entered: \n%s" % (input_sent)

#this creates the phrase dictionary as a global variable--takes phrase:phrase type tuples
p_dict = {}

#updates p_dict with tuples entered by the user in levtwomain()
def p_dict_addition(a,b):
	p_dict.update({a:b})

#shows the user what they've entered so far and loops back through the update function if 
#the user wants to input more tuples; once the user is finished adding tuples, this
#function calls a function that allows the user to start over	
def add_ptag():	
	print "Here are the syntactic constituents you've entered so far: "
	print p_dict
	
	p_add = raw_input ("Are there other syntactic constituents that need to be labeled? ")
	
	if p_add == "1":
		levtwomain()
	else:
		print "Here are the syntactic constituents you've entered for the sentence: "
		print p_dict
		levtwocheck()

#allows the user to clear the current dictionary and start the constituent labeling 
#process over		
def levtwocheck():
	dict_accuracy = raw_input("Are these correct? ")
	current_dict = p_dict
	
	if dict_accuracy == "0":
		current_dict.clear()
		print "Let's start over."
		levtwomain()
	else:
#HERE WE NEED TO ADD THE FUNCTION THAT SENDS THE constituent_token:constituent_type 
#TUPLES IN THE DICTIONARY TO THE SYNTACTIC CONSTITUENT TABLE IN THE DATABASE
        for phrase in p_dict.keys():
            dict_cur.execute("SELECT id FROM phrases WHERE phrase='{0}');".format(phrase))
            phraseID = int(dict_cur.fetchone())
            if not phraseID:
                dict_cur.execute("INSERT INTO phrases(phrase, phrase_type) VALUES (%s,%s)",(phrase, p_dict[phrase]))
                dict_cur.execute("SELECT id FROM phrases WHERE phrase='{0}');".format(phrase))
                phraseID = int(dict_cur.fetchone())
            #dict_cur.execute("INSERT INTO phrases_sentences(sentenceID, phraseID) VALUES (%i, %i)", (sentenceID, phraseID)
		print "Great! Now let's identify some grammatical functions in the sentence."

def levtwomain():
#gets a constituent from the user and assigns it to variable "p"
	p = raw_input ("Please enter a syntactic constituent in this sentence: ")
#gets a constituent type from the user and assigns it to variable "p_tag"
	p_tag = raw_input ("What kind of constituent is this? ")
#calls the function that adds the p_dict{} entering "p" and "p_tag" for "a" and "b"
	p_dict_addition(p, p_tag)
#calls the function that allows the user to update p_dict{}
	add_ptag()
	
#calls the main function
levtwomain()

#****************** LEVEL 3 *********************************************************

print """Now you're going to identify the grammatical functions for the constituents in your sentence."""
print "Here are the syntactic constituents you labeled in the last step: "
print p_dict

#this creates a dictionary for grammatical functions
gramfunc_dict = {}

#this asks the user to identify the grammatical subject, labels it "subject" and adds
#this key:value pair to the gramfunc_dict
def label_gramsub():
	gram_sub = raw_input ("Which constituent is the grammatical subject of the sentence? ")
	gramfunc_dict.update({gram_sub:"subject"})
	dirobj_loop()

#this asks the user to identify the grammatical direct object, labels it "direct object" 
#and adds this key:value pair to the gramfunc_dict	
def label_gramdirobj():
	gram_dirobj = raw_input ("""Which constituent is the grammatical direct object of the sentence? """)
	gramfunc_dict.update({gram_dirobj:"direct object"})
	indobj_loop()

#this asks the user to identify the grammatical indirect object, labels it "indirect object" 
#and adds this key:value pair to the gramfunc_dict	
def label_gramindobj():
	z = gramfunc_dict
	gram_indobj = raw_input ("""Which constituent is the grammatical indirect object of the sentence? """)
	gramfunc_dict.update({gram_indobj:"indirect object"})
	print """Here are the grammatical functions you've assigned to the constituents in your sentence: """
	print z
	confirm_gramfunc()

#this asks the user if there is a grammatical subject in the sentence
#if the answer is no, the user is asked about direct grammatical objects with "dirobj_loop()"
#if the answer is yes "1", the subject labeling function "label_gramsub()" is called
def sub_loop():
	subj_exist = raw_input ("Does this sentence have a grammatical subject? ")
	if subj_exist == "1":
		label_gramsub()
	else:
		dirobj_loop()

#this asks the user if there is a grammatical direct object in the sentence
#if the answer is no, the user is asked about indirect grammatical objects with "indobj_loop()"
#if the answer is yes, "1", the direct object labeling function "label_gramdirobj()" is called
def dirobj_loop():
	dirobj_exist = raw_input ("Does this sentence have a grammatical direct object? ")
	if dirobj_exist == "1":
		label_gramdirobj()
	else:
		indobj_loop()

#this asks the user if there is a grammatical indirect object in the sentence
#if the answer is no, the user is displayed the grammatical function labeling for the
#sentence and asked whether it's correct
def indobj_loop():
	x = gramfunc_dict
	indobj_exist = raw_input ("Does this sentence have a grammatical indirect object? ")
	if indobj_exist == "1":
		label_gramindobj()
	else:
		print """Here are the grammatical functions you've assigned to the constituents in your sentence: """
		print x
		confirm_gramfunc()

#this function shows the tuples in gramfunc_dict to the user ask asks whether it's correct
#if no "0", the current dictionary is deleted and levthreemain() function is called again
#if yes, the tuples from gramfunc_dict are send to a grammatical function table for the 
#session
def confirm_gramfunc():
	y = gramfunc_dict
	gf_confirmation = raw_input ("Are these correct? ")
	
	if gf_confirmation == "0":
		y.clear()
		print "Let's start over. "
		levthreemain()
#HERE WE NEED TO SEND THE "grammatical function:phrase" TUPLES IN gramfunc_dict TO THE
#GRAMMATICAL FUNCTION TABLE FOR THIS SESSION	
	else:
        for word in gramfunc_dict.keys():
            # this is not going to work as a dictionary since we are losing the ordering, which is important for our databasing.
            # we should change it to a list of tuples, or something...or, probably, an ordered dictionary!
            #this is a placeholder
            colname ="wordtype1"
            dict_cur.execute(""" UPDATE words SET '{0}' = '{1}' WHERE word='{2}';""".format(colname,gramfunc_dict[word],word ))
#WE NEED TO FIGURE OUT WHAT TO SHOW THE USER AT THIS POINT and how to show them
#e.g., show the phrase structure rules and the syntactic tree for the sentence
		print """Great! Now let's take a look at all the information you've entered for the following sentence: """
		print input_sent
		print "syntactic constituents: %r" % p_dict
		print "grammatical functions: %r" % gramfunc_dict
	
#this defines the function order for levthreemain()
def levthreemain():
	sub_loop()

#this calls the main function for collecting level three (grammatical function) data	
levthreemain()