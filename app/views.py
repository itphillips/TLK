
#imports the app variable from the app package
from app import app, db, lm, oid 
from flask import render_template, url_for, request, redirect, jsonify, flash, session, g
from flask.ext.login import login_user, logout_user, current_user, login_required
#imporst class 'LoginForm' from forms.py
from .forms import LoginForm, EnterSentenceForm, TagPOSForm
from .models import User, Sentence, Word

#this function loads a user from the db and is used by flask-login
@lm.user_loader #this decorator registers the function with flask-login
def load_user(id):
	return User.query.get(int(id))


@app.before_request
def before_request():
	g.user = current_user


@app.route('/')
@app.route('/home')
def home():
	return render_template("home.html",
							title='Home')


#view function that renders the login template by passing the form object LoginForm(Form)
#to the template login.html
#methods arguments tell Flask that this view function accespts GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler #tells flask-openid that htis is our login view function
def login():
	#this sees if the user is logged in, if so it won't do a second login
	#g global is set up by flask as a place to store and share data during the life
	#of a request - this stores the logged in user
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('user', username=g.user.username))
	#instantiated object from LoginForm()
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data #stores the value of 
		#remember_me boolean in flask session (not db.session!)
		#once data is stored in the session object, it will be avaialble during 
		#that request and any future requests made by the same client
		#data remains there until explicitly removed - flask keeps a different
		#session container for each client of the app

		#this triggers user authentication through flask-openid
		#takes 2 arguments: openid given by user in web form and a list of 
		#data items we want from openid provider
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])

		# flash('Login requested for OpenID="%s", remember_me=%s' %
		# 	(form.openid.data, str(form.remember_me.data)))
		# return redirect('/home')

	return render_template('login.html',
							title='Sign In',
							form=form,
							#grabs configuration by looking it up in app.config with 
							#its key, then adds array to render_template call as a 
							#template argument
							providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp): #resp argument contains information returned by openid provider
	#this if statement is for validation
	#user cannot login if email is not provided
	if resp.email is None or resp.email == "":
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email=resp.email).first()

	#searches db for email provided - adds new user to db if email is not found
	if user is None:
		username = resp.nickname
		if username is None or username == "":
			username = resp.email.split('@')[0]
		user = User(username=username, email=resp.email)
		db.session.add(user)
		db.session.commit()
	remember_me = False

	#loads remember_me value from flask session (stored in login view function)
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)

	#registers that this is a valid login
	login_user(user, remember = remember_me)

	#redirects to 'next' page or user-specific homepage, if next page not provided by request
	#next, meaning the page the user wants to see after logging in (e.g., they tried
	#to visit a user-specific page, but were stopped b/c they need to be logged in; 
	#after logging in, this page should appear)
	return redirect(request.args.get('next') or url_for('user', username=g.user.username))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route('/user/<username>')
@login_required #ensures this page is only seen by logged in users
def user(username):
	#first() returns the first result and discards the rest
	user = User.query.filter_by(username=username).first()
	if user == None:
		flash('User %s not found.', (username))
		return redirect(url_for('login'))
	#queries the db for all sentences from user and assigns them to 'sentences' 
	sentences = g.user.sentences.all()
	return render_template('user.html',
							user=user,
							sentences=sentences)


@app.route('/input_sentence', methods=['GET', 'POST'])
@login_required
def input_sentence():
	form = EnterSentenceForm()
	if form.validate_on_submit():
		sentence = Sentence(sentence=form.sentence.data, 
							author=g.user, 
							english_gloss=form.english_gloss.data, 
							language=form.language.data)
		db.session.add(sentence)
		db.session.commit()
		# flash('Your changes have been saved!')
		return redirect(url_for('user', 
								username=g.user.username))
	# 	# return redirect(url_for('confirm_sentence'))
	return render_template("input_sentence.html",
							form=form)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
	sentence = Sentence.query.get(id)
	if sentence is None:
		flash('Sentence not found!')
		return redirect(url_for('user', 
								username=g.user.username))
	if sentence.author.id != g.user.id:
		flash('You cannot delete this sentence!')
		return redirect(url_for('user', 
								username=g.user.username))
	db.session.delete(sentence)
	db.session.commit()
	# flash('Your sentence has been deleted.')
	return redirect(url_for('user', 
							username=g.user.username))


@app.route('/tagPOS/<sentence>', methods=['GET', 'POST'])
@login_required
def tagPOS(sentence):
	form = TagPOSForm()

	# sentence = sentence
	user = request.args.get("user")
	english_gloss = request.args.get("english_gloss")
	language = request.args.get("language")
	sentence_id = request.args.get("sentence_id")
	# if form.validate_on_submit():
	if request.method == "POST":
		for word in sentence.split():
			print word

			word = Word(word=word,
					partofspeech=form.partofspeech.data,
					sentence_id=sentence_id)
		
			db.session.add(word)
			db.session.commit()

	 	return render_template("test.html", 
	 							sentence=sentence)

	return render_template("tagPOS.html",
							sentence=sentence, 
							user=user,
							english_gloss=english_gloss,
							language=language,
							sentence_id=sentence_id,
							form=form)


#this is a page that can be used as a placeholder during development
@app.route('/test/<int:id>', methods=['GET', 'POST'])
@login_required #ensures this page is only seen by logged in users
def test(id):
	sentence = Sentence.query.get(id)
	user = g.user #passes g.user down to the template
	return render_template('test.html',
							sentence=sentence)


