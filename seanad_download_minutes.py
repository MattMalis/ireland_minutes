import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup

urls_csv = open('ireland_seanad_single_date_urls.csv')

def download_single_day(day_address):
	end_index = day_address.find('?opendocument')
	if end_index==-1:
		print 'ERROR' ## FIX ME
	workable_url = day_address[:end_index-3] 
	## workable_url takes three additional digits at end, to specify page# (there won't be >999 pages)


path='/Users/iramalis/Desktop/ireland-seanad-minutes/'+yr+'/'+mo+'/'+dd+'/'
if os.path.exists(path)==False:
	os.makedirs(path)
	
## HOW TO IDENTIFY VOTE TABLES?
## eg, see 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/seanad1975060500004?opendocument'
## Amendment put.

# The Committee divid ed: Tá, 14; Níl, 24.

# ^^ what to do about typos...
## maybe search for reg ex, 'Ta, \d; Nil, \d'?
## for that example - the vote table is the only <td class="tbr"> tag

## 'Question Put', 'Amendment Put', 'Question Declared ___',...
## 'Ta,' ?
## search for any one of the above - if file contains one, downlaod