import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup
#from odf.opendocument import OpenDocumentText
#from odf.text import P


## all of the individual day URLs are actually opendocument format...
# had to install odfpy
## https://pypi.python.org/pypi/odfpy
## NEVERMIND just need to add "http://"


urls_csv = open('seanad_single_date_urls.csv')
url_reader = csv.reader(urls_csv)

single_days = list(url_reader)
#cur = 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2016051700001?opendocument'

## adding http:// to each day's url, and appending the number of pages as the last col of the day row
for day in single_days[1:]:
	try:
		day_url = 'http://' + day[-1]
		day_page = urllib2.urlopen(day_url)
		day_soup = BeautifulSoup(day_page.read(), "html.parser")
		day_txt = str(day_soup)
		select_index = day_txt.find('</select>')
		num_index = select_index + len('</select> of ')
		endex = day_txt[num_index:].find('\n')
		n_pages = day_txt[num_index:num_index+endex]
		day[-1] = day_url
		day.append(n_pages)
		#print "num_index: %s, endex: %s, n_pages: %s" %(num_index,endex,n_pages)
	except:
		print "ERROR WITH ptI %s%s%s" %(day[0],day[1],day[2])
		time.sleep(random.uniform(0,5))
		continue

print "completed part I"

c = open('seanad_urls_pages.csv', 'wb')
c_writer = csv.writer(c)
c_writer.writerow(["Year", "Month", "Day", "URL", "NumPages"])

for day in single_days[1:]:
	try:
		c_writer.writerow(day)
	except:
		print "ERROR WITH ptII %s%s%s" %(day[0],day[1],day[2])
		time.sleep(random.uniform(0,5))
		continue

print "completed part II"

c.flush()
c.close()

urls_csv.flush()
urls_csv.close()
