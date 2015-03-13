#I'm using this to test out Lev 3 functions before adding them to Lev1main.py
#levtwomain is called here because it creates phrase_dict, which is needed to run 
#levthreemain
import string
import collections


input_sent = raw_input("Please enter one sentence with all punctuation: ")


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
gramfunc_dict = collections.OrderedDict()

#this asks the user to identify the grammatical subject, labels it "subject" and adds
#this key:value pair to the gramfunc_dict
def label_gramsub():
	gram_sub = raw_input ("Which constituent is the grammatical subject of the sentence? ")
	gramfunc_dict.update({"subject":gram_sub})
	dirobj_loop()

#this asks the user to identify the grammatical direct object, labels it "direct object" 
#and adds this key:value pair to the gramfunc_dict	
def label_gramdirobj():
	gram_dirobj = raw_input ("""Which constituent is the grammatical direct object of the sentence? """)
	gramfunc_dict.update({"direct object":gram_dirobj})
	indobj_loop()

#this asks the user to identify the grammatical indirect object, labels it "indirect object" 
#and adds this key:value pair to the gramfunc_dict	
def label_gramindobj():
	z = gramfunc_dict
	gram_indobj = raw_input ("""Which constituent is the grammatical indirect object of the sentence? """)
	gramfunc_dict.update({"indirect object":gram_indobj})
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