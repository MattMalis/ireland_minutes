import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup


seanad_yr_base_address = 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=seanad&year='

seanad_yr_addresses = {}
for yr in range(1922,2017):
	seanad_yr_addresses[yr] = seanad_yr_base_address + str(yr)
	
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
for yr in seanad_yr_addresses.keys():
	try:
		all_date_addresses[yr] = find_one_years_addresses(seanad_yr_addresses[yr]) ## function defined above
	except:
		print "Error with find_one_years_addresses() for yr: %s" %(yr)
		time.sleep(random.uniform(0,5))
		pass

### FINDING NUMBER OF PAGES FOR EACH DATE, appending to that date's list 
###			(which contains the dat's page1 URL and is stored as a value in the all_date_addresses dict)
for yr in all_date_addresses.keys():
	for mo in all_date_addresses[yr].keys():
		if all_date_addresses[yr][mo] is None:
			continue
		for d in all_date_addresses[yr][mo].keys():
			try:	
				date_url = all_date_addresses[yr][mo][d][0]
				date_page = urllib2.urlopen(date_url)
				date_soup = BeautifulSoup(date_page.read(), "html.parser")
				date_txt = str(date_soup)
				## number of pages is always found after a </select> tag
				select_index = date_txt.find('</select>')
				num_index = select_index + len('</select> of ')
				endex = date_txt[num_index:].find('\n')
				n_pages = date_txt[num_index:num_index+endex]
				## for each date, appending the num_pages to the end of a list which previously contained only the URL for the 
				## 		first page of that date
				all_date_addresses[yr][mo][d].append(n_pages)
			except: 
				print "Error getting page numbers for: %s, %s, %s" %(yr, mo, d)
				time.sleep(random.uniform(0,5))
				pass


## writing csv
c = open('seanad_single_date_urls.csv', 'wb')
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
				print "ERROR: couldn't write: %s%s%s" %(yr,m,d)
				pass
				
c.flush()
c.close()

 