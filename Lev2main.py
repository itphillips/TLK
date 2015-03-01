#I'm using this to test out Lev 2 functions before adding them to Lev1main.py

import string

input_sent = raw_input("Please enter one sentence with all punctuation: ")


#this contains the functions needed to collect and store TLK level 2 data

print "Now we're going to identify the syntactic categories in the sentence."
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