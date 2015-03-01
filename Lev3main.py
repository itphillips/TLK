#I'm using this to test out Lev 3 functions before adding them to Lev1main.py
#levtwomain is called here because it creates phrase_dict, which is needed to run 
#levthreemain
import string

input_sent = raw_input("Please enter one sentence with all punctuation: ")


#this contains the functions needed to collect and store TLK level 2 data

print "Now we're going to identify the syntactic constituents in the sentence."
print "Here is the sentence you entered: \n%s" % (input_sent)

#this creates the phrase dictionary as a global variable
phrase_dict = {}

#this function gets the user to enter a phrasal/syntactic constituent and label its category
#it then adds the phrase and category into the phrase_dict as a key:value pair
def phrase_tag():
	p = raw_input ("Please enter a syntactic constituent in the sentence: ")
	ptag = raw_input ("What kind of constituent is this? ")
	phrase_dict.update({p:ptag})


#this function shows the user the phrasal divisions that have been created so far and 
#asks if there are any more
#if the answer is 'yes' it loops back through lev2main(); if 'no' ...
def add_ptag():	
	print "Here are the syntactic constituents you've entered so far: "
	print phrase_dict
	
	p_add = raw_input ("Are there other syntactic constituents that need to be labeled?")
	
	if p_add == "1":
		levtwomain()
	else:
		print "Here are the syntactic constituents you've entered for the sentence:"
		print phrase_dict
		
#this function shows the tuples in phrase_dict to the user ask asks whether they are correct
#if no "0", the current dictionary is deleted and levtwomain() function is called again
#if yes, the tuples from phrase_dict are send to a syntactic constituent table for the 
#session and moves to level 3
def confirm_ptag():
	a = phrase_dict
	ptag_confirmation = raw_input("Are these correct?")
	
	if ptag_confirmation == "0":
		del a
		levtwomain()
#HERE WE NEED TO SEND THE p:p_tag PAIRS IN phrase_dict TO THE TABLE FOR THIS SESSION	
	else:
		print "Great! Now let's identify some grammatical functions in the sentence." 
	
#this function runs the phrase_tag and confirm_ptag functions, above
def levtwomain():
	phrase_tag()
	add_ptag()
	confirm_ptag()

#this calls the main lev 2 function	
levtwomain()

#****************** LEVEL 3 *********************************************************

print "Now you're going to identify the grammatical functions for the constituents in your sentence."
print "Here are the syntactic constituents you labeled in the last step:"
print phrase_dict

#this creates a dictionary for grammatical functions
gramfunc_dict = {}

#this asks the user to identify the grammatical subject, labels it "subject" and adds
#this key:value pair to the gramfunc_dict
def label_gramsub():
	gram_sub = raw_input ("Which constituent is the grammatical subject of the sentence?")
	gramfunc_dict.update({gram_sub:"subject"})
	dirobj_loop()

#this asks the user to identify the grammatical direct object, labels it "direct object" 
#and adds this key:value pair to the gramfunc_dict	
def label_gramdirobj():
	gram_dirobj = raw_input ("Which constituent is the grammatical direct object of the sentence?")
	gramfunc_dict.update({gram_dirobj:"direct object"})
	indobj_loop()

#this asks the user to identify the grammatical indirect object, labels it "indirect object" 
#and adds this key:value pair to the gramfunc_dict	
def label_gramindobj():
	gram_indobj = raw_input ("Which constituent is the grammatical indirect object of the sentence?")
	gramfunc_dict.update({gram_indobj:"indirect object"})
	confirm_gramfunc()

#this asks the user if there is a grammatical subject in the sentence
#if the answer is no, the user is asked about direct grammatical objects with "dirobj_loop()"
#if the answer is yes "1", the subject labeling function "label_gramsub()" is called
def sub_loop():
	subj_exist = raw_input ("Does this sentence have a grammatical subject?")
	if subj_exist == "1":
		label_gramsub()
	else:
		dirobj_loop()

#this asks the user if there is a grammatical direct object in the sentence
#if the answer is no, the user is asked about indirect grammatical objects with "indobj_loop()"
#if the answer is yes, "1", the direct object labeling function "label_gramdirobj()" is called
def dirobj_loop():
	dirobj_exist = raw_input ("Does this sentence have a grammatical direct object?")
	if dirobj_exist == "1":
		label_gramdirobj()
	else:
		indobj_loop()

#this asks the user if there is a grammatical indirect object in the sentence
#if the answer is no, the user is displayed the grammatical function labeling for the
#sentence and asked whether it's correct
def indobj_loop():
	b = gramfunc_dict
	indobj_exist = raw_input ("Does this sentence have a grammatical indirect object?")
	if indobj_exist == "1":
		label_gramindobj()
	else:
		print "Here are the grammatical functions you've assigned to the constituents in your sentence: "
		print b

#this function shows the tuples in gramfunc_dict to the user ask asks whether it's correct
#if no "0", the current dictionary is deleted and levthreemain() function is called again
#if yes, the tuples from gramfunc_dict are send to a grammatical function table for the 
#session
def confirm_gramfunc():
	c = gramfunc_dict
	gf_confirmation = raw_input ("Are these correct?")
	
	if gf_confirmation == "0":
		del c
		levthreemain()
#HERE WE NEED TO SEND THE "grammatical function:phrase" TUPLES IN gramfunc_dict TO THE
#GRAMMATICAL FUNCTION TABLE FOR THIS SESSION	
	else:
#WE NEED TO FIGURE OUT WHAT TO SHOW THE USER AT THIS POINT and how to show them
#e.g., show the phrase structure rules and the syntactic tree for the sentence
		print "\nGreat! Now let's take a look at all the information you've entered for this sentence:"
		print phrase_dict
		print gramfunc_dict
	
#this defines the function order for levthreemain()
def levthreemain():
	sub_loop()
	confirm_gramfunc()

#this calls the main function for collecting level three (grammatical function) data	
levthreemain()