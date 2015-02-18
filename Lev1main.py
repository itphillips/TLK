#this contains the functions needed to collect and store TLK level 1 metadata

import string

#This function asks the user to input a sentence
def get_sent():
    a = raw_input("Please enter one sentence with all punctuation: ") 
    return a

#This function splits the sentence into individual words; replaces punctuation with a space
#This function needs to be revised so that contractions get split in the right place
#before "n't", not at "'"

#this converts caps to lowercase
def sent_cleanup(whole_sent):
    words = string.lower(whole_sent)

#This loop goes through all of these characters and if that character is in the main file, 
#it replaces it with a space (for easier splitting)
    for punct in ["!", "'", '"', ":", "\n", ";", ".", ",", "?", "$", "(", ")", "-"]:
        words = string.replace(words, punct, " ")
    	b = string.split(words, " ")
    return b

#this function creates a dictionary called "sentence_dict"
def tag_pos(input_sent):
    sentence_dict = {}
    
#This loop goes through all of the words in the input and asks what the part-of-speech tag
#should be, then adds this value-key pair to the dictionary "sentence_dict"
    for word in input_sent:
        print "What part of speech does '" + word + "' belong to?"
        b = raw_input(" ")
        sentence_dict.update({word:b})
    return sentence_dict

#this function checks the info that the user has entered; it re-runs tag_pos() if the info
#is incorrect; it asks for a new sentence if the info is correct
def pos_confirm():
	confirmation = raw_input("Is this information correct?")
	if confirmation == "0":
		tag_pos()
	else:
		print "Great! Let's continue."
		levonemain()

#this function runs all of the small functions (above) that are needed to gather TLK
#Level 1 (part-of-speech) data
def levonemain():
#this variable is the whole sentence that the user inputs
	whole_sent = get_sent()
#this variable is the output of sent_cleanup when performed on whole_sent
	split_sent = sent_cleanup(whole_sent)
#this variable is the output of tag_pos when performed on split_sent
	pos_tags = tag_pos(split_sent)
	
#this prints the dictionary that contains each word in the sentence input by the user
#and the POS tag that the user has applied to each word 
	print pos_tags
	


#this calls the main Level 1 function: starts with a whole sentence input by the user
#and ends by adding each word and its part-of-speech tag to the dictionary sentence_dict
levonemain()