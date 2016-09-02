import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup

seanad_base_address = 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/seanad'

# 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/seanad' + 'YYYYMMDD' + '000' + ['01' through end (eg '56')]
# bottom right, on main page for specific date - 'page 1 of __' (50, 56, eg)
# '01' is the main page for date; '02' is prelude, etc...


# looks like every vote starts with: 'The Seanad divided'

# number of pages: '</select> of XX' --dropdown menu, XX will be the last page -- these are the only </select> tags on the page

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
		date_addresses[dd] = base_address+path
	return date_addresses


def find_date_addresses(yr_address):
	yr_page = urllib2.urlopen(yr_address)
	yr_soup = BeautifulSoup(yr_page.read(), "html.parser")
	yr_txt = str(yr_soup)
	addresses_by_month = {}
	for m in months:
		this_months_addresses = find_one_months_addresses(m, yr_txt, 'oireachtasdebates.oireachtas.ie')
		addresses_by_month[m] = this_months_addresses
	return addresses_by_month

all_date_addresses = {}
for yr in seanad_yr_addresses.keys():
	all_date_addresses[yr] = find_date_addresses(seanad_yr_addresses[yr])
	

 