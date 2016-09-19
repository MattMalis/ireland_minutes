import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup

print 'starting'
## this is an exact copy of seanad_urls.py, just with 'seanad' replaced with 'dail'

dail_yr_base_address = 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=dail&year='

dail_yr_addresses = {}
## ran it first time from 1922-2017 (seanad starts at 1922), then realized dail starts at 1919, ran a second time for 1919-1922
#for yr in range(1919,1922):
#for yr in range(1922,2017):

##to do it all at once:
for yr in range(1919,2017):
	dail_yr_addresses[yr] = dail_yr_base_address + str(yr)

print 'got the years'
## from main year page: all 'opendocument' strings are in a link to a new date's minutes
## also, looks like every month name appears exactly once (unless there are no minutes from that month, eg august sometimes)

## pattern, on the main year page: 
## Month
## href link to individual day address, with path after 'oireachtasdebates.oireachtas.ie', 
##		followed by >DD<
## align='"center"
## next month
## (four center tags before first month)

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December'] 

## function, takes as args:
## 		month (string, capitalized)
## 		text for a single year's main page html,
## 		base url, for the individual dates' paths to be appended to
## returns:
##		dict whose keys are the dates (strings of format 'dd') for which there are legislative minutes,
##			and whose values are the URLs for a specific date's minutes
print 'function1'
def find_one_months_addresses(month, yr_text, base_address):
	date_addresses = {}
	m_index = yr_text.find(month)
	if m_index==-1:
		return None
	end_index = yr_text[m_index:].find('align="center"') ## this is found at the end of each month's row on the table
	href_indices = [h.start() for h in re.finditer('href',yr_text[m_index:m_index+end_index])]
	for i in href_indices:
		path_begin_index = m_index + i + 6 ## 6 = length of string 'href="'
		path_end_index = yr_text[path_begin_index:].find('">')
		path = yr_text[path_begin_index:path_begin_index+path_end_index]
		dd = yr_text[path_begin_index+path_end_index+2:path_begin_index+path_end_index+4] ## each link ends with >DD<
		date_addresses[dd] = [base_address+path]
	return date_addresses

## takes a year's main page address, calls on function above, returns a dict of the following form:
## 		keys: months
##		values: keys, representing dates for which there are minutes
##				values: individual date URLs
print 'function2'
def find_one_years_addresses(yr_address):
	yr_page = urllib2.urlopen(yr_address)
	yr_soup = BeautifulSoup(yr_page.read(), "html.parser")
	yr_txt = str(yr_soup)
	addresses_by_month = {}
	for m in months:
		this_months_addresses = find_one_months_addresses(m, yr_txt, 'http://oireachtasdebates.oireachtas.ie')
		addresses_by_month[m] = this_months_addresses
	return addresses_by_month

## creating a master dict with all individual date URLs for every year
all_date_addresses = {}
for yr in dail_yr_addresses.keys():
	print 'pt1 yr: %s' %(yr)
	try:
		all_date_addresses[yr] = find_one_years_addresses(dail_yr_addresses[yr])
	except:
		print "Error with find_one_years_addresses() for yr: %s" %(yr)
		time.sleep(random.uniform(0,5))
		pass
print 'finished find_one_year_addresses()'

for yr in all_date_addresses.keys():
	print 'starting with yr: %s' %(yr)
	for mo in all_date_addresses[yr].keys():
		if all_date_addresses[yr][mo] is None:
			continue
		for d in all_date_addresses[yr][mo].keys():
			try:	
				date_url = all_date_addresses[yr][mo][d][0]
				date_page = urllib2.urlopen(date_url)
				date_soup = BeautifulSoup(date_page.read(), "html.parser")
				date_txt = str(date_soup)
				select_index = date_txt.find('</select>')
				#print "select_index: %s" %(select_index)
				num_index = select_index + len('</select> of ')
				#print "num_index: %s" %(num_index)
				endex = date_txt[num_index:].find('\n')
				#print "endex: %s" %(endex)
				n_pages = date_txt[num_index:num_index+endex]
				#print "n_pages: %s" %(n_pages)
				all_date_addresses[yr][mo][d].append(n_pages)
			except: 
				print "Error getting page numbers for: %s, %s, %s" %(yr, mo, d)
				time.sleep(random.uniform(0,5))
				pass


## writing csv

## patch-up for 1919-1922, after i already ran it with 1922-2017
#c = open('dail_single_date_urls_earliest.csv', 'wb')
#for full thing:
c = open('dail_single_date_urls.csv','wb')
c_writer = csv.writer(c)
c_writer.writerow(["Year", "Month", "Day", "URL", "NumPages"])

for yr in all_date_addresses.keys():
	for m in all_date_addresses[yr].keys():
		if all_date_addresses[yr][m] is None:
			continue
		for d in all_date_addresses[yr][m].keys():
			try:
				c_writer.writerow([yr, m, d, all_date_addresses[yr][m][d][0], all_date_addresses[yr][m][d][1] ])
			except:
				print "couldn't write: %s%s%s" %(yr,m,d)
				
c.flush()
c.close()

 