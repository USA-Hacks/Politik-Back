from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
from newspaper import Article
import json

from ml.naive_bayes import NaiveBayes

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://politik:politik@localhost/politik_db'
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = "user"
	id = db.Column(db.String(64), primary_key=True)
	viewings = db.relationship('Viewing', backref='user', lazy='dynamic')
	leaning = db.Column(db.Float)	

	def __init__(self, id):
		self.id = id
		self.leaning = 0

	def __repr__(self):
		return '<User %r>' % self.id

class Viewing(db.Model):
	__tablename__ = "viewing"
	id = db.Column(db.Integer, primary_key=True)	
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'))
	url = db.Column(db.String(1024))
		
	def get_weighted_score(self):
		return self.ml_score * self.user_score

class PoliticalSite(db.Model):
	__tablename__ = "political_site"

	id = db.Column(db.Integer, primary_key=True)
	site_url = db.Column(db.String(1024))
	leaning = db.Column(db.Float)


def get_nlp_data(url):
	article = Article(url)
	article.download()
	article.parse()
	article.nlp()
	
	return json.dumps(article.keywords)

def get_article_text(url):
	try:
		article = Article(url)
		article.download()
		article.parse()
	
		return article.text
	except:
		return None

def get_a_score(a_url):
	users = User.query.filter(User.viewings.any(url=a_url)).all()
	metric = 0
	for user in users:
		metric += user.leaning
	if len(users):
		metric = metric / len(users)
	return metric

@app.route('/get_keywords', methods=['POST'])
def get_keywords():
	data = json.loads(request.data)
	
	return jsonify(keywords=get_nlp_data(data['url']))

@app.route('/get_total_score', methods=['POST'])
def get_total_score():
	data = json.loads(request.data)

	user = db.session.query(User).filter(User.id == data['id'])	
	if not user.count():
		return jsonify(success=False)
	else:
		user = user.one()	
	
	# Return Core User Group here
	if abs(user.leaning) > 0.25:
		return jsonify(score=user.leaning)

	metric = 0
	for view in user.viewings:
		metric += get_a_score(view.url)
	return jsonify(score=metric)		

@app.route('/calc_score', methods=['POST'])
def calc_score():
	data = json.loads(request.data)
	
	metric = get_a_score(data['url'])	
	'''text = get_article_text(data['url'])
	if text != None:
		nb = NaiveBayes()
		leaning = nb.get_leaning(text)
	'''

	return jsonify(ascore=metric)

@app.route('/store_view', methods=['POST'])
def store_view():
	data = json.loads(request.data)
	
	if not db.session.query(User).filter(User.id == data['id']).count():
		new_user = User(data['id'])
		db.session.add(new_user)
		db.session.commit()

	views = db.session.query(Viewing) \
			.filter(Viewing.url == data['url']) \
			.filter(Viewing.user_id == data['id'])
	
	if not views.count():
		new_view = Viewing()
		new_view.user_id = data['id']
		new_view.url = data['url']

		db.session.add(new_view)
		db.session.commit()

	
	user = db.session.query(User).filter(User.id == data['id']).first()
	if not user:
		return jsonify(success=False)		
	
	user_score = 0
	pol_len = 0
	urls = [view.url for view in user.viewings]
	
	pols = PoliticalSite.query.all()
	for pol in pols:
		for url in urls:
			if pol.site_url in url:
				user_score += pol.leaning
				pol_len += 1
	if pol_len:
		user_score = user_score / pol_len
		user.leaning = user_score

	db.session.commit()

	return jsonify(success=True)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80)
