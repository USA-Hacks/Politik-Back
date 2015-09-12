from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
from newspaper import Article
import predictionio
import json
import math

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://politik:politik@localhost/politik_db'
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = "user"
	id = db.Column(db.String(64), primary_key=True)
	viewings = db.relationship('Viewing', backref='user', lazy='dynamic')

	def __init__(self, id):
		self.id = id

	def __repr__(self):
		return '<User %r>' % self.id

class Viewing(db.Model):
	__tablename__ = "viewing"
	id = db.Column(db.Integer, primary_key=True)	
	user_id = db.Column(db.String(64), db.ForeignKey('user.id'))
	url = db.Column(db.String(1024))
	user_score = db.Column(db.Integer)
	ml_score = db.Column(db.Float)
	
	def get_weighted_score(self):
		return self.ml_score * self.user_score

@app.route('/get_article_leaning', methods=['POST'])
def get_article_leaning():
	data = json.loads(request.data)

	results = get_ml_data(data['url'])	

	return jsonify(**results)

def get_ml_data(url):
	article = Article(url)
	article.download()
	article.parse()
	article.nlp()

	article = (article.summary).encode('utf-8').strip()
	
	ec = predictionio.EngineClient()
	results = ec.send_query({'text': article})

	if math.isnan(results['confidence']):
		results['confidence'] = 0
	
	return results

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
	results = get_ml_data(data['url'])
	if not views.count():
		new_view = Viewing()
		new_view.user_id = data['id']
		new_view.url = data['url']
		new_view.user_score = (data['score'] * 2) - 1
		new_view.ml_score =  resuluts['confidence']

		db.session.add(new_view)
		db.session.add(commit)
	

		return jsonify(success=True)
	else:
		view = views.first()
		view.user_score = (data['score'] * 2) - 1
		return jsonify(success=True)

@app.route('/calc_leaning', methods=['POST'])
def calc_leaning():
	data = json.loads(request.data)
	result = 0
	
	viewings = Viewing.query.filter_by(user_id=data['id']).all()
	for viewing in viewings:
		result += viewing.get_weighted_score()
	if len(viewings):
		result = result / len(viewings)
	
	return jsonify(value=result)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80)
