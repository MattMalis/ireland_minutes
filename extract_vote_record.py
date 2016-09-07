import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup

Legislator_Votes = {}

class Vote ():
	def __init__ (self, date, vote_id, question = '', tas = [], nils = []):
		self.date = date
		self.vote_id = vote_id
		self.question = question
		self.tas = tas
		self.nils = nils

class Legislator ():
	def __init__ (self, name, ta_votes = [], nil_votes = [], first_vote_year = 1922, last_vote_year = 2016):
		self.name = name
		self.ta_votes = ta_votes
		self.nil_votes = nil_votes
		self.first_vote_year = first_vote_year
		self.last_vote_year = last_vote_year
		
	def __eq__(self, other):
		if self.name==other.name:
			return True
		typo_count = 0
		for i in range(len(self.name)):
			if self.name[i] != other.name[i]:
				typo_count += 1
			
		