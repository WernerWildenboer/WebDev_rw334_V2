####################################  Setup  ####################################

from flask import Flask, request, session, redirect, url_for, render_template, flash
import os

app = Flask(__name__)

from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from datetime import datetime
import uuid
from urllib.parse import urlparse, urlunparse

################################  Database Link  ################################

authenticate("hobby-ogikmifabjnfgbkeflkddeal.dbs.graphenedb.com:24780", "cs334", "b.soC0X1oY5V3W.npSyseCrhtODLqgc")
graph = Graph("https://hobby-ogikmifabjnfgbkeflkddeal.dbs.graphenedb.com:24780/db/data/", bolt = False)

def create_uniqueness_constraint(label, property):
	query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
	query = query.format(label=label, property=property)
	graph.run(query)

create_uniqueness_constraint("User", "username")
create_uniqueness_constraint("Topic", "name")
create_uniqueness_constraint("Question", "id")
create_uniqueness_constraint("Answer", "id")


##################################  Functions  ##################################

class User:
	def __init__(self, username):
		self.username = username

	def find(self):
		user = graph.find_one("User", "username", self.username)
		return user
	
	def register(self, email, password):
		if not self.find():
			user = Node("User", username=self.username, email=email, password=bcrypt.encrypt(password))
			graph.create(user)
			return True
		else:
			return False
			
	def verify_password(self, password):
		user = self.find()
		if user:
			return bcrypt.verify(password, user['password'])
		else:
			return False
			
	def add_question(self, text, topics):
		user = self.find()
		question = Node(
			"Question",
			id=str(uuid.uuid4()),
			text=text,
			timestamp=timestamp(),
			date=date()
		)
		rel = Relationship(user, "ASKED", question)
		graph.create(rel)

		topics = [x.strip() for x in topics.lower().split(',')]
		for t in set(topics):
			topic = graph.merge_one("Topic", "name", t)
			rel = Relationship(topic, "TAGGED", question)
			graph.create(rel)
            return True
			
	def follow_topic(self, name):
		user = self.find()
		topic = graph.find_one("Topic", "name", name)
		rel = Relationship(user, "FOLLOWING", topic)
		
	def answer_question(self, question, answer):
		user = self.find()
		question = graph.find_one("Question", "id", question)
		answer = Node(
			"Answer",
			id=str(uuid.uuid4()),
			text=answer,
			timestamp=timestamp(),
			date=date()
		)
		rel = Relationship(user, "WROTE", answer)
		graph.create(rel)
		rel = Relationship(answer, "TO", question)
		graph.create(rel)
			
def timestamp():
	epoch = datetime.utcfromtimestamp(0)
	now = datetime.now()
	delta = now - epoch
	return delta.total_seconds()

def date():
	return datetime.now().strftime('%Y-%m-%d')

	
####################################  Views  ####################################

@app.route('/')
def index():
	return render_template('index.html', title="Quora-lite")

@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'POST':
		email = request.form['email']
		username = request.form['username']
		password = request.form['psw']
		if len(email) < 1:																# Proper email checks
			flash('Your email must be at least one character.')
		if len(username) < 1:															# better username checks?
			flash('Your username must be at least one character.')
		elif len(password) < 5:															# better password checks?
			flash('Your password must be at least 5 characters.')
		elif not User(username).register(email, password):								# Should probably have separate checks for username and email
			flash('A user with that username or email already exists.')
		else:
			session['username'] = username
			flash('Logged in.')
			return redirect(url_for('index'))

	return render_template('register.html', title="Register")
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['psw']

		if not User(username).verify_password(password):
			flash('Invalid login.')
		else:
			session['username'] = username
			flash('Logged in.')
			return redirect(url_for('index'))

	return render_template('login.html', title="Login")
	
@app.route('/add_question', methods=['POST'])
def add_question():
	text = request.form['question']
	topics = request.form['topics']

	if not text:
		flash('You must give your question text.')
	else:
		User(session['username']).add_question(text, topics)

	return redirect(url_for('index'))
	
@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logged out.')
	return redirect(url_for('index'))
	
@app.route('/changePassword')
def changePassword():
	return render_template('Changepsw.html', title="Change Password")
	
@app.route('/profile/<username>')
def profile(username):
	return render_template('Profile.html', title="Profile", username=username)
	
@app.route('/followTopic/<topic>')
def followTopic(topic):
	User(session['username']).follow_topic(topic)
	return redirect(request.referrer)
	
@app.route('/answer/<question>')
def answer(question):
	answer = request.form['answer']
	User(session['username']).answer_question(question, answer)
	return redirect(request.referrer)
	
@app.route('/question/<question>')
def question(question):
	question = graph.find_one("Question", "id", question)
	return render_template('Question.html', title="Question", question=question)

	
###################################  Run app  ###################################


port = int(os.environ.get('PORT', 5000))
app.secret_key = os.urandom(24)
app.run(host='0.0.0.0', port=port)