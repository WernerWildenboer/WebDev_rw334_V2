####################################  Setup  ####################################

from flask import Flask, request, session, redirect, url_for, render_template, flash
import os, time

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
			user = Node("User", username=self.username, email=email, password=bcrypt.encrypt(password), Uploaded_pp="0", bio='')
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
		rel = Relationship(user, "FOLLOWS", topic)
		graph.create(rel)
        
	def follow_user_function(self, name):
		user1 = self.find()
		user2 = graph.find_one("User", "username", name)
		rel = Relationship(user1, "FOLLOWS", user2)
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
		rel = Relationship(user, "ANSWERED", question)
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
			user = User(session['username']).find()
			session['uploaded'] = user.properties['Uploaded_pp']
			flash('Logged in.')
			return redirect(url_for('index'))

	return render_template('login.html', title="Login")

#================================================================================
@app.route('/change_password',methods=['GET', 'POST'])
def change_password():
	if request.method == 'POST':
		password_old = request.form['password_old']
		password_new = request.form['password_new']
		username = session['username']

		if not User(username).verify_password(password_old):
			flash('Invalid login.')
		else:
			
			
			password = password_new
			query ='''MATCH (n:User)
            WHERE n.username='{username}'
            SET n.password = "{password_q}"'''
			query = query.format(username=session['username'],password_q=bcrypt.encrypt(password))
			
			change_password = graph.run(query)
			return redirect(url_for('index'))
        
	return render_template('change_password.html', title="Change Password")

#================================================================================
	
@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
	query ='''MATCH (topic:Topic) RETURN topic.name as name ORDER BY topic.name DESC;'''
	topcs = graph.run(query)
	if request.method == 'POST':
		text = request.form['add_question_box']
		topics = request.form['topics']

		if not text:
			flash('You must give your question text.')
		else:
			User(session['username']).add_question(text, topics)

	return render_template('add_question.html', topics=topcs)
	
@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logged out.')
	return redirect(url_for('index'))
	
@app.route('/forgotPassword')
def forgotPassword():
	return render_template('forgot_password.html', title="Forgot Password")

@app.route('/profile/<username>')
def profile(username):
	user = User(username).find()
	session['bio'] = user.properties['bio']
	return render_template('profile.html', title="Profile", username=username)
#========================================================================	
@app.route('/followTopic/<topic>')
def followTopic(topic):
	User(session['username']).follow_topic(topic)
	return redirect(request.referrer)
#=====================================================================	
@app.route('/add_answer/<question>', methods=['GET', 'POST'])
def add_answer(question):
	if request.method == 'POST':
		answer = request.form['add_answer_box']
		User(session['username']).answer_question(question, answer)
	return render_template('add_answer.html', question=question)
	
@app.route('/question/<question>')
def question(question):
	id = question
	query = "MATCH (q:Question) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) WHERE ID(q) = {question} RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, count(answer) as answers, collect(tpc) as topics, askedby.username as askedby, count(upvotes) as upvote ORDER BY timestamp DESC LIMIT 1;"
	query = query.format(question=question)
	question = graph.run(query)
	query = "MATCH (q:Question)<-[:TO]-(answer:Answer)<-[:WROTE]-(user:User) OPTIONAL MATCH (answer)<-[upvote:UPVOTE]-() WHERE ID(q) = {question} RETURN answer.text As text, ID(answer) as id, answer.timestamp as timestamp, count(upvote) as upvotes, user.username AS username ORDER BY upvotes DESC LIMIT 1000;"
	query = query.format(question=id)
	answers = graph.run(query)
	return render_template('question.html', title="Question", question=question, answers=answers)

@app.route('/upvote/<answer>')
def upvote(answer):
	user = User(session['username']).find()
	answer = graph.node(int(answer))
	rel = Relationship(user, "UPVOTE", answer)
	graph.create(rel)
	return redirect(request.referrer)

@app.route('/search', methods=['GET', 'POST'])
def search():
	if request.method == 'POST':
		search_string = request.form['search_string_from_user']
		query ='''MATCH (n:User)
WHERE toLower(n.username) =~ toLower('.*{search_string}.*')
RETURN n AS user'''
		query = query.format(search_string=search_string)
		list_usernames = graph.run(query)
		return render_template('search.html', title="Users", list_usernames=list_usernames)
	return render_template('search.html', title="Users")



#=====================================*_ | Follow | _START_*===================================
@app.route('/follow_user/<user>')
def follow_user(user):	
	if 1 :
		query ='''MATCH (a:User),(b:User)
WHERE a.username = '{user_1}' AND b.username = '{user_2}'
CREATE (a)-[r:FOLLOWS]->(b)
RETURN a,b,r;'''
		query = query.format(user_1=session['username'],user_2=user)
		follows = graph.run(query)
		  
		return render_template('search.html', title="Users", follows =follows )
    
	return render_template('search.html', title="Users" )
#=====================================*_ | Follow | _END_*=====================================
@app.route('/show_topics')
def show_topics():
	query = "MATCH ()<-[n:TAGGED]-(topic:Topic) WITH topic.name as name, count(n) AS rank RETURN name, rank ORDER BY rank DESC;"
	topics = graph.run(query)
	return render_template('show_topics.html', topics=topics)
	
@app.route('/show_suggestions')
def show_suggestions():
    query ='''MATCH a=((user_1:User)-[r1:FOLLOWS]->(user_2:User)-[r2:FOLLOWS]->(user_3:User))
WHERE user_1.username <> user_3.username
AND NOT (user_1)-[:FOLLOWS]->(user_3) AND user_1.username = '{username}'
MATCH (user_3)-[:WROTE]->()<-[upvotes:UPVOTE]-()
RETURN user_3.username AS name,COUNT(upvotes) AS rank ORDER BY rank DESC;'''
    query = query.format(username=session['username'])
    suggestions = graph.run(query)
    return render_template('show_suggestions.html', suggestions=suggestions)



@app.route('/show_bookmarked')
def show_bookmarked():
    query ='''MATCH (user1:User)-[r1:BOOKMARK]->(q:Question)
    WHERE user1.username='{username}' RETURN q AS bookmarked_q, ID(q) as id;'''
    query = query.format(username=session['username'])
    bookmarked = graph.run(query)
    return render_template('show_bookmarked.html', bookmarked=bookmarked)
	
@app.route('/user/<username>')
def user(username):
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
			
			userSession = session['username']
			temp = userSession + ".jpg"
			full_filename = os.path.join(app.config['UPLOAD_FOLDER'], temp)
			file.save(full_filename)

			query ='''MATCH (n:User) WHERE n.username='{usernameQry}' SET n.Uploaded_pp = 1;'''
			query = query.format(usernameQry=userSession)
			session['uploaded'] = "1"
			upload_image = graph.run(query)
			return render_template('profile.html', title="Profile")
        
#================================================================================

@app.route('/change_bio', methods=['POST'])
def change_bio():
	if request.method == 'POST':
		bio = request.form['bio']
		session['bio'] = bio
		user = User(session['username']).find()
		user['bio'] = bio
		user.push()
	return redirect(request.referrer)
#================================================================================		

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/topic/<topic>')
def topic(topic):
	return render_template('topic.html', topic=topic)
	
@app.route('/show_questions/<type>/<amount>/<qa>', defaults={'topic': None})
@app.route('/show_questions/<type>/<amount>/<qa>/<topic>')
def show_questions(type, amount, qa, topic):
	japie = qa
	if (qa == 'qa'):
		qa = 'ASKED|ANSWERED|TAGGED'
	elif (qa == 'q'):
		qa = 'ASKED|TAGGED'
	else:
		qa = 'ANSWERED'
	if (type == 'mainSignedOutTime'):
		query = "MATCH (q:Question) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, count(answer) as answers, count(upvotes) as upvote ORDER BY timestamp DESC LIMIT {amount};"
		query = query.format(amount=amount)
		questions = graph.run(query)
	elif (type == 'mainSignedOutUpvote'):
		query = "MATCH (q:Question) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, count(answer) as answers, count(upvotes) as upvote ORDER BY upvote DESC LIMIT {amount};"
		query = query.format(amount=amount)
		questions = graph.run(query)
	elif (type == 'mainSignedInTime'):
		query = "MATCH (q:Question)<-[r:{qa}]-(n)<-[:FOLLOWS]-(me:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[bookmarked:BOOKMARKED]-(me) WHERE me.username = '{username}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, n as reason, type(r) AS type, count(answer) as answers, count(bookmarked) as bookmark, count(upvotes) as upvote ORDER BY timestamp DESC LIMIT {amount};"
		query = query.format(username=session['username'], amount=amount, qa=qa)
		questions = graph.run(query)
	elif (type == 'mainSignedInUpvote'):
		query = "MATCH (q:Question)<-[r:{qa}]-(n)<-[:FOLLOWS]-(me:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[bookmarked:BOOKMARKED]-(me) WHERE me.username = '{username}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, n as reason, type(r) AS type, count(answer) as answers, count(bookmarked) as bookmark, count(upvotes) as upvote ORDER BY upvote DESC  LIMIT {amount};"
		query = query.format(username=session['username'], amount=amount)
		questions = graph.run(query)
	
	elif (type == 'topicTime'):
		query = "MATCH (q:Question)<-[:TAGGED]-(topic:Topic) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer) WHERE topic.name = '{topic}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, count(answer) as answers ORDER BY timestamp DESC LIMIT {amount};"
		query = query.format(topic=topic, amount=amount)
		questions = graph.run(query)
		
	# Questions for a single topic ordered by upvotes
	elif (type == 'topicUpvote'):
		query = "MATCH (q:Question)<-[:TAGGED]-(topic:Topic) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer) WHERE topic.name = '{topic}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, count(answer) as answers ORDER BY upvote DESC LIMIT {amount};"
		query = query.format(topic=topic, amount=amount)
		questions = graph.run(query)
		
	# Questions for a single user ordered by time uploaded
	elif (type == 'userTime'):
		query = "MATCH (q:Question)<-[r:{qa}]-(user:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer) WHERE user.username = '{topic}' RETURN DISTINCT ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, type(r) AS type, count(answer) as answers ORDER BY timestamp DESC LIMIT {amount};"
		query = query.format(topic=topic, amount=amount, qa=qa)
		questions = graph.run(query)
		
	# Questions for a single user ordered by upvotes
	elif (type == 'userUpvote'):
		query = "MATCH (q:Question)<-[r:{qa}]-(user:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer) OPTIONAL MATCH (q)<-[:TO]-()-[upvotes:UPVOTE]-() WHERE user.username = '{topic}' RETURN DISTINCT ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, type(r) AS type, count(answer) as answers, count(upvotes) as upvote ORDER BY upvote DESC LIMIT {amount};"
		query = query.format(topic=topic, amount=amount, qa=qa)
		questions = graph.run(query)
	elif (type == 'topicsTime'):
		query = "MATCH (q:Question)<-[:TAGGED]-(topic:Topic)<-[:FOLLOWS]-(me:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[bookmarked:BOOKMARKED]-(me) WHERE me.username = '{username}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, count(answer) as answers, count(bookmarked) as bookmark, count(upvotes) as upvote ORDER BY timestamp DESC LIMIT {amount};"
		query = query.format(amount=amount)
		questions = graph.run(query)
	elif (type == 'topicsUpvote'):
		query = "MATCH (q:Question)<-[:TAGGED]-(topic:Topic)<-[:FOLLOWS]-(me:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[bookmarked:BOOKMARKED]-(me) WHERE me.username = '{username}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, count(answer) as answers, count(bookmarked) as bookmark, count(upvotes) as upvote ORDER BY upvote DESC LIMIT {amount};"
		query = query.format(amount=amount)
		questions = graph.run(query)
	elif (type == 'usersTime'):
		query = "MATCH (q:Question)<-[r:{qa}]-(n:User)<-[:FOLLOWS]-(me:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[bookmarked:BOOKMARKED]-(me) WHERE me.username = '{username}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, n as reason, type(r) AS type, count(answer) as answers, count(bookmarked) as bookmark, count(upvotes) as upvote ORDER BY timestamp DESC LIMIT {amount};"
		query = query.format(username=session['username'], amount=amount, qa=qa)
		questions = graph.run(query)
	elif (type == 'usersUpvote'):
		query = "MATCH (q:Question)<-[r:{qa}]-(n:User)<-[:FOLLOWS]-(me:User) OPTIONAL MATCH (q)<-[:TAGGED]-(tpc:Topic) OPTIONAL MATCH (q)<-[:ASKED]-(askedby:User) OPTIONAL MATCH (q)<-[:TO]-(answer:Answer)<-[upvotes:UPVOTE]-(:User) OPTIONAL MATCH (q)<-[bookmarked:BOOKMARKED]-(me) WHERE me.username = '{username}' RETURN distinct ID(q) as id, q.text as text, q.timestamp as timestamp, collect(DISTINCT tpc) as topics, askedby.username as askedby, n as reason, type(r) AS type, count(answer) as answers, count(bookmarked) as bookmark, count(upvotes) as upvote ORDER BY upvote DESC LIMIT {amount};"
		query = query.format(username=session['username'], amount=amount, qa=qa)
		questions = graph.run(query)
	return render_template('show_questions.html', questions=questions, type=type, qa=japie)
	
@app.route('/bookmark/<question>')
def bookmark(question):
	user = User(session['username']).find()
	question = graph.node(int(question))
	rel = Relationship(user, "BOOKMARK", question)
	graph.create(rel)
	return redirect(request.referrer)
	
@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s)
	
###################################  Run app  ###################################


port = int(os.environ.get('PORT', 5000))
app.secret_key = os.urandom(24)

app.run(host='0.0.0.0', port=port, debug=True)
