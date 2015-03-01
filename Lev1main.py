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
            dict_cur.execute("INSERT INTO words(word, pos, language) VALUES (%s,%s, %s)",(word, pos_tags[word],"english"))
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

print "Now you're going to identify the syntactic categories in the sentence."
print "Here is the sentence you entered: \n%s" % (input_sent)

#this creates the phrase dictionary as a global variable
phrase_dict = {}

#this function gets the user to enter a phrasal/syntactic constituent and label its category
#it then adds the phrase and category into the phrase_dict as a key:value pair
def phrase_tag():
	p = raw_input ("Please enter a phrasal constituent in the sentence: ")
	ptag = raw_input ("What kind of phrase is this? ")
	phrase_dict.update({p:ptag})

#this function shows the user the phrasal divisions that have been created so far and 
#asks if there are any more
#if the answer is 'yes' it loops back through lev2main(); if 'no' it sends the key:value
#pairs in the dictionary to the database and moves to level 3
def confirm_ptag():	
	print "Here are the phrases you've entered so far: "
	print phrase_dict
	
	p_confirmation = raw_input ("Are there other phrasal constituents that need to be labeled?")
	
	if p_confirmation == "1":
		levtwomain()
#HERE WE NEED TO SEND THE p:p_tag PAIRS IN phrase_dict TO THE TABLE FOR THIS SESSION	
	else:
		print "Great! Now let's identify some grammatical functions in the sentence." 
		
#this function runs the phrase_tag and confirm_ptag functions, above
def levtwomain():
	phrase_tag()
	confirm_ptag()

#this calls the main lev 2 function	
levtwomain()

#****************** LEVEL 3 *********************************************************

#working on this in Lev3main.py
#will add lev 3 functions here once they are up and running in Lev3main.py

