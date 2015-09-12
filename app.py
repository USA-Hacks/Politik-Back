from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/user'
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = "user"
	id = db.Column(db.String(32), primary_key=True)
	viewings = db.relationship('Viewing', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % self.id

class Viewing(db.Model):
	__tablename__ = "viewing"
	user_id = db.Column(db.String(32), db.ForeignKey('user.id'))
	url = db.Column(db.String(1024))
	score = db.Column(db.Integer)

@app.route('/leaning')
def leaning():
	ret = {
		'leaning': 'Democrat',
		'score': 1.3
	}
	return jsonify(**ret)

if __name__ == '__main__':
	app.debug = True
	app.run()
