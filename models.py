from app import db

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
