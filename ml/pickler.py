#!/usr/bin/python

from __future__ import division
import json
import math
import cPickle as pickle
from collections import Counter
import unicodedata
import sys

#output_filename = 'republicans.pickle'
output_filename = 'democrats.pickle'

#input_filename = './data/theblaze.json'
input_filename = './data/thedailybeast.json'

tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))
def strip_punctuation(text):
    return text.translate(tbl)

f = open(input_filename, 'r')
lines = f.readlines()

words = []
for line in lines:
	data = json.loads(line)
	paragraph = data['properties']['text']
	words += [strip_punctuation(word) for word in paragraph.split()]

words = Counter(words)
total = sum(words.values())

for word in words:
	words[word] = math.log(words[word] / total)

pickle.dump (words, open(output_filename, 'wb'))
f.close()

