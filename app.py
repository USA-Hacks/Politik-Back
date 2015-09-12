from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from newspaper import Article
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/user'
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = "user"
	id = db.Column(db.String(32), primary_key=True)
	viewings = db.relationship('Viewing', backref='user', lazy='dynamic')

	def __init__(self, id):
		self.id = id

	def __repr__(self):
		return '<User %r>' % self.id

class Viewing(db.Model):
	__tablename__ = "viewing"
	user_id = db.Column(db.String(32), db.ForeignKey('user.id'))
	url = db.Column(db.String(1024))
	user_score = db.Column(db.Integer)
	ml_score = db.Column(db.Float)
	
	def get_weighted_score(self):
		return self.ml_score * self.user_score
		
@app.route('/get_article_body', methods=['POST'])
def get_article_body():
	data = json.loads(request.data)

	article = Article(data['url'])
	article.download()
	article.parse()

	return jsonify(text=article.text)

@app.route('/edit_view', methods=['POST'])
def edit_view():
	data = json.loads(request.data)
	
	try:
		view = Viewing.query.filter_by(user_id=data['id']).filter_by(url=data['url']).first()
	except:
		return jsonify(success=False)
		
	view.user_score = data['score']
	return jsonify(success=True)

@app.route('/store_view', methods=['POST'])
def store_view():
	data = json.loads(request.data)
	
	if not db.session.query(User).filter(User.id == data['id']).count():
		new_user = User(data['id'])
		db.session.add(new_user)
		db.session.commit()

	view_count = db.session.query(Viewing) \
			.filter(Viewing.url == data['url']) \
			.filter(Viewing.user_id == data['id']) \
			.count()

	if not view_count:
		new_view = Viewing()
		new_view.user_id = data['id']
		new_view.url = data['url']
		new_view.user_score = data['score']
		new_view.ml_score = 1 # Needs to be PredictionIO call

		db.session.add(new_view)
		db.session.add(commit)
	

		return jsonify(success=True)
	else:
		return jsonify(success=False)

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
	app.run()
