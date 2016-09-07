import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup

from seanad_download_all_minutes import download_page, same_date_next_page
## this is an exact copy of dail_urls.py, just with 'seanad' replaced with 'dail'

urls_csv = open('dail_single_date_urls.csv')
url_reader = csv.reader(urls_csv)

single_days = list(url_reader)

urls_csv.close()


#e.g.: 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2016051700001?opendocument'
## replace the three digits before '?opendocument' with the appropriate digits to indicate page number

# 
# def download_page(address,path,filename,wait=.5):
# 	time.sleep(random.uniform(0,wait))
# 	page = urllib2.urlopen(address)
# 	page_content = page.read()
# 	with open(path+filename, 'w') as p_html:
# 		p_html.write(page_content)

## function takes as args: 
##		the url for the first page of a given date; 
## 		the page number you want to download
##		the index of the character in the url where the 3-digit page number begins
## 			(this should be the same for all dates and pages)
## returns:
## 		modified url with the desired page number
# def same_date_next_page(date_p1_url, page_num, page_num_index):
# 	workable_url = date_p1_url[:page_num_index] 
# 	## workable_url takes three additional digits at end, to specify page# (there won't be >999 pages)
# 	p3 = '' # p3 will be a 3-char string indicating page number
# 	if len(str(page_num))==1:
# 		p3 = '00%s'%(page_num)
# 	if len(str(page_num))==2:
# 		p3 = '0%s'%(page_num)
# 	if len(str(page_num))==3:
# 		p3 = str(page_num)
# 	updated_url = workable_url+p3 + '?opendocument'
# 	return updated_url

## grabbing the index for the same_date_next_page() function
day1_url = single_days[1][3]
page_num_index_all_urls = day1_url.find('?opendocument') - 3



ticker = 0
for day in single_days[1:]: #row 0 is the column names
	ticker+=1
	if ticker%100==0:
		print "downloading: %s" %(ticker)
	day_path='/Users/iramalis/Desktop/ireland-dail-minutes/%s/%s/%s/'%(day[0],day[1],day[2])
	if os.path.exists(day_path)==False:
		os.makedirs(day_path)
	for pp in range(1,int(day[-1])+1):
		try:
			f_name = 'Ireland-dail-minutes-%s%s%s-p%s.html'%(day[0],day[1],day[2],pp)
			p_address = same_date_next_page(day[3], pp, page_num_index_all_urls)
			download_page(p_address,day_path,f_name,.5)
		except:
			print "ERROR DOWNLOADING %s%s%s, page #%s" %(day[0],day[1],day[2],pp)
			time.sleep(random.uniform(0,5))
			pass

	