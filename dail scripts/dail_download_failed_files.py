#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup

## reading in a txt file that contains the printed error messages from running dail_download_all_minutes.py

file = open('dail_error_files.txt')
errors = file.readlines()

base_url = 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail'
months = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11','December':'12'}

def make_url(base_url, error_line):
	pattern = re.compile(r'(?P<year>\d+)(?P<month>\D+)(?P<day>\d+)\D+(?P<pages>\d+)')
	srch = pattern.search(error_line)
	url_dict = srch.groupdict()
	month_num = months[url_dict['month']]
	page_num = ''.join('0'*(5-len(url_dict['pages']))) + url_dict['pages']
	url = base_url + url_dict['year']+month_num+url_dict['day']+page_num
	url_info = [url, url_dict['year'], month_num, url_dict['day'], url_dict['pages']]
	return url_info
	
#example URL: 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2016051700001'
#example error line: 'ERROR DOWNLOADING 2000April12, page #77'

url_infos = []
for e in errors:
	try:
		url_infos.append(make_url(base_url, e))
	except:
		print 'failed to make url for: %s' %(e)
		pass

def download_page(address,path,filename,wait=.1):
	time.sleep(random.uniform(0,wait))
	page = urllib2.urlopen(address)
	page_content = page.read()
	with open(path+filename, 'w') as p_html:
		p_html.write(page_content)


for u in url_infos:
	try:
		day_path = '/Users/apple/Desktop/ireland-dail-minutes/%s/%s/%s/'%(u[1], [m for m in months.keys() if months[m]==u[2]][0], u[3])
		if os.path.exists(day_path)==False:
			os.makedirs(day_path)
	except:
		print 'failed to set day_path for: %s' %(url_infos)
		pass
	try:
		f_name = 'Ireland-dail-minutes-%s%s%s-p%s.html'%(u[1], [m for m in months.keys() if months[m]==u[2]][0], u[3], u[4])
		p_address = u[0]
		download_page(p_address,day_path,f_name,.1)
	except:
		print "ERROR DOWNLOADING %s%s%s, page #%s" %(u[1], u[2], u[3], u[4])
		time.sleep(random.uniform(0,5))
		pass

	