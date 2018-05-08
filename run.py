####################################  Setup  ####################################

from flask import Flask, request, session, redirect, url_for, render_template, flash
import os

#UPLOAD_FOLDER = 'app/static/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'img')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from datetime import datetime
import uuid
from urllib.parse import urlparse, urlunparse
from werkzeug.utils import secure_filename
from flask import send_from_directory

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
			topic = graph.find_one("Topic", "name", t)
			if not topic:
				topic = Node("Topic", name=t)
			rel = Relationship(topic, "TAGGED", question)
			graph.create(rel)
			
	def follow_topic(self, name):
		user = self.find()
		topic = graph.find_one("Topic", "name", name)
		rel = Relationship(user, "FOLLOWING", topic)
		graph.create(rel)
		
	def answer_question(self, question, answer):
		user = self.find()
		question = graph.node(int(question))
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
		
	# def get_timeline(self):
		
	
	# def get_topics(self):
		
	
	# def get_suggestions(self):
		
		
			
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
	return render_template('index.html', title="What He Said")

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
	
@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
	if request.method == 'POST':
		text = request.form['add_question_box']
		topics = request.form['topics']

		if not text:
			flash('You must give your question text.')
		else:
			User(session['username']).add_question(text, topics)

	return render_template('add_question.html')
	
@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logged out.')
	return redirect(url_for('index'))
	
@app.route('/changePassword')
def changePassword():
	return render_template('change_password.html', title="Change Password")

@app.route('/forgotPassword')
def forgotPassword():
	return render_template('forgot_password.html', title="Forgot Password")

@app.route('/profile/<username>')
def profile(username):
	return render_template('profile.html', title="Profile", username=username)
	
@app.route('/followTopic/<topic>')
def followTopic(topic):
	if has_key(session['username']):
		User(session['username']).follow_topic(topic)
	return redirect(request.referrer)
	
@app.route('/add_answer/<question>', methods=['GET', 'POST'])
def add_answer(question):
	if request.method == 'POST':
		answer = request.form['add_answer_box']
		User(session['username']).answer_question(question, answer)
	return render_template('add_answer.html', question=question)
	
@app.route('/question/<question>')
def question(question):
	question = graph.find_one("Question", "id", question)
	return render_template('question.html', title="Question", question=question)
	
@app.route('/search')
def search():
	return render_template('search.html', title="Search")

@app.route('/show_topics')
def show_topics():
	topics = []
	query = "MATCH ()<-[n:TAGGED]-(topic:Topic) WITH topic.name as name, count(n) AS rank RETURN name, rank ORDER BY rank DESC;"
	topics = graph.run(query)
	return render_template('show_topics.html', topics=topics)
	
@app.route('/show_suggestions')
def show_suggestions():
	suggestions = []
	query = "MATCH ()<-[n:TAGGED]-(topic:Topic) WITH topic.name as name, count(n) AS rank RETURN name, rank ORDER BY rank DESC;"
	suggestions = graph.run(query)
	return render_template('show_suggestions.html', suggestions=suggestions)
	
@app.route('/user')
def user():
	return render_template('user.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file')
			return redirect(request.url)

		file = request.files['file']

		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)

		if file and allowed_file(file.filename):
			#filename = secure_filename(file.filename)
			#latestfile.save(os.path.join(app.root_path, app.config['STATIC_FOLDER'], 'customlogos', 'logo.png'))
			#uploads//app/static/img/userTemp.png
			#http://sleepy-plains-17562.herokuapp.com/static/img/userTemp.png
			full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'userTemp.jpg')
			file.save(full_filename)
			return "successfully uploaded"
			#redirect(url_for('uploaded_file', filename=full_filename))
		#return render_template('profile.html', title="Profile", username=session.username)

	
		
		
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/topic/<topic>')
def topic(topic):
	#questions = get_questions(topic)
	return render_template('topic.html', topic=topic)
	
###################################  Run app  ###################################


port = int(os.environ.get('PORT', 5000))
app.secret_key = os.urandom(24)
app.run(host='0.0.0.0', port=port, debug=True)
