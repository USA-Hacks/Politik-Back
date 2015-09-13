import math
import cPickle as pickle

class NaiveBayes():
	def strip_punctuation(self, text):
		return "".join(c for c in text if c not in ('!','.',':'))
	
	def __init__(self):
		democrats = pickle.load(open('democrats.pickle', 'rb'))
		republicans = pickle.load(open('republicans.pickle', 'rb'))

	def get_leaning(self, text):
		words = [strip_punctuation(word) for word in text.split()]
	
		dem_score = 0
		rep_score = 0
		for word in words:
			if word in democrats:
				dem_score += democrats[word]
			if word in republicans:
				rep_score += republicans[word]
	
		diff = abs(dem_score - rep_score)
		if diff > 60:
			return 'Democrat'
		else:
			return 'Republican'
