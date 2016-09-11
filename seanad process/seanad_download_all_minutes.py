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
ticker = 0
## adding http:// to each day's url, and appending the number of pages as the last col of the day row
for day in single_days[1:]:
	ticker+=1
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
		if ticker%100==0:
			print "ptI: %s" %(ticker)
		#print "num_index: %s, endex: %s, n_pages: %s" %(num_index,endex,n_pages)
	except:
		print "ERROR WITH ptI %s%s%s" %(day[0],day[1],day[2])
		time.sleep(random.uniform(0,5))
		continue

print "\n\ncompleted part I\n\n"

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

print "\n\ncompleted part II\n\n"

c.flush()
c.close()

urls_csv.flush()
urls_csv.close()

### closed the csv's, now re-opening
cc = open('seanad_urls_pages.csv')
cc_reader = csv.reader(cc)
days = list(cc_reader)

## looking through each page for a given day, finding whether it has a table; if so, return it (as one url in a list)
def find_vote_table_pages(day_row):
	day_url_p1 = day_row[-2]
	#print day_url_p1
	end_index = day_url_p1.find('?opendocument')
	#print end_index
	if end_index==-1:
		print 'ERROR ptIII' ## FIX ME
	workable_url = day_url_p1[:end_index-3] 
	## workable_url takes three additional digits at end, to specify page# (there won't be >999 pages)
	pages = day_row[-1]
	pages_with_tables = {}
	for p in range(1,int(pages)+1):
		if len(str(p))==1:
			p3 = '00%s'%(p)
		if len(str(p))==2:
			p3 = '0%s'%(p)
		if len(str(p))==3:
			p3 = str(p)
		this_page = workable_url+p3 + '?opendocument'
		this_page_html = urllib2.urlopen(this_page)
		this_page_soup = BeautifulSoup(this_page_html.read(), 'html.parser')
		page_txt = str(this_page_soup)
		## look for some things that indicate theres a vote
		ta_index = page_txt.find('T\xc3\xa1,') ## 'Ta' with the accent
		nil_index = page_txt.find('N\xc3\xadl,') ## 'Nil' with the accent
		table_index = page_txt.find('<td class="tbr">')
		if set([ta_index, nil_index, table_index])==set([-1]) :
			continue
		pages_with_tables[p] = this_page
	day_row.append(pages_with_tables)



def download_page(address,path,filename,wait=5):
	time.sleep(random.uniform(0,wait))
	page = urllib2.urlopen(address)
	page_content = page.read()
	with open(path+filename, 'w') as p_html:
		p_html.write(page_content)

ticker = 0
for day in days[1:]: #row 1 is the column names
	ticker+=1
	try:
		if ticker%100==0:
			print "ptIV: %s" %(ticker)
		find_vote_table_pages(day)
		if len(day[-1])==0:
			continue
		day_path='/Users/iramalis/Desktop/ireland-seanad-minutes/%s/%s/%s/'%(day[0],day[1],day[2])
		if os.path.exists(day_path)==False:
			os.makedirs(day_path)
		for pp in day[-1].keys():
			f_name = 'Ireland-seanad-minutes-%s%s%s-p%s.html'%(day[0],day[1],day[2],pp)
			p_address = day[-1][pp]
			download_page(p_address,day_path,f_name,5)
	except:
		print "ERROR WITH ptIV %s%s%s" %(day[0],day[1],day[2])
		time.sleep(random.uniform(0,5))
		continue

	
## HOW TO IDENTIFY VOTE TABLES?
## eg, see 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/seanad1975060500004?opendocument'
## Amendment put.

# The Committee divid ed: Ta[a'], 14; Ni[i']l, 24.

# ^^ what to do about typos...
## maybe search for reg ex, 'Ta, \d; Nil, \d'?
## for that example - the vote table is the only <td class="tbr"> tag

## 'Question Put', 'Amendment Put', 'Question Declared ___',...
## 'Ta,' ?
## search for any one of the above - if file contains one, downlaod