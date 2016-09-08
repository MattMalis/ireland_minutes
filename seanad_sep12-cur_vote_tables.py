#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import urllib2
import datetime
import time
import random
import os
import unicodecsv as csv
import re
from bs4 import BeautifulSoup
import codecs

### Run this script after all legislative minutes have already been downloaded,
##		and are stored as html files in directories of the form 
##			/Desktop/ireland-seanad-minutes/YYYY/MonthName/DD

print '\n\n\n\n\n\n\n\n'


base_path = '/Users/iramalis/Desktop/ireland-seanad-minutes/'

def import_one_day_htmls(yr, mo, day):
	try:
		if not isinstance(day,str):
			day = str(day)
		if len(day)==1:
			day = '0'+day
		day_folder = base_path+'%s/%s/%s'%(yr, mo, day)
		file_names = os.listdir(day_folder)
		return file_names
	except:
		print 'ERROR in import_one_day_htmls(%s, %s, %s)'%(yr,mo,day)
		pass


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December'] 

c = open('seanad_sep12-cur_votes.csv', 'wb')
c_writer = csv.writer(c)
c_writer.writerow(["Year", "Month", "Day", "Vote #", "Subject", "Result","Ta/Nil","Legislators"])

cc = open('seanad_sep12-cur_nonRC.csv','wb')
cc_writer = csv.writer(cc, encoding = 'utf-8')

for yr in range(2012,2013): ## newest web format runs from sep2012 through present
	this_yr_months = os.listdir(base_path+str(yr))
	for mo in this_yr_months: 
		if mo == '.DS_Store':
			continue
		if yr==2012:
			if mo not in ['October', 'November']:#['September', 'October', 'November']:#, 'December']:
				continue
		this_months_days = os.listdir(base_path+str(yr)+'/'+mo)
		for day in this_months_days:
			print '\n TODAY: %s%s%s' %(yr,mo,day)
			if day == '.DS_Store':
				continue
			day_ticker = 0
			#print '\n TODAY: %s%s%s' %(yr,mo,day)
			day_file_names = import_one_day_htmls(yr, mo, day)
			#print '#htmls: %s' %len(day_file_names)
			#one_day_vote_tables = []
			for f_name in day_file_names:
				one_file_vote_tables = []
				page = open(base_path+str(yr)+'/'+mo+'/'+day+'/'+f_name)
				soup = BeautifulSoup(page.read(), 'html.parser')
				title = soup.find_all('title')
				#str_title = str(title)
				str_title = ''
				for t in title:
					str_title = t.encode()
				begindex = str_title.find(' - ') + len(' - ')
				endex = str_title[begindex:].find('</title>')
				subject = ''
				if begindex!=-1 and endex!=-1:
					subject = str_title[begindex:begindex+endex]
				all_p_center = soup.find_all('p',{'class':['pcentre']})#('p')#,{'p class':'pcentre'})
				result = ''
				for p in all_p_center:
					p_txt = p.get_text()
					if p_txt.find('declared')!=-1 and p_txt.find(' put ')==-1:
						if len(p_txt)<=100:
							result = p_txt
							#print result
				all_p = soup.find_all('p')
				p_not_center = [p for p in all_p if p not in all_p_center]
				for p in all_p:
					p_txt = p.get_text()
					if p_txt.find('question')!=-1 or p_txt.find('amendment')!=-1:
						if len(p_txt)<=100:
							print f_name
							print 'non-RC: %s' %(p_txt)
							cc_writer.writerow([yr,mo,day,p_txt.encode()])
				tables = soup.find_all('table')
				for t in range(len(tables)):
					if len(tables[t].find_all('table'))!=0:
						#print 'table in a table! day: %s%s%s' %(yr,mo,day)
						one_file_vote_tables.extend(tables[t].find_all('table'))
				for i in range(0,len(one_file_vote_tables)):
					#if (i==0):
						#print 'len(one_file_vote_tables): %s'%(len(one_file_vote_tables))
					try:
						#print 'i: %s' %i
						vt = one_file_vote_tables[i]
						ta_vote_tds = vt.find_all('td',{'bgcolor':'#ccffcc'}) 
						nil_vote_tds = vt.find_all('td',{'bgcolor':'#ffcccc'})			
						ta_names = []
						for row in ta_vote_tds:
							#s_row = str(row)
							s_row = row.encode()
							begindex = s_row.find('pid=')
							if begindex==-1:
								continue
							endex = s_row[begindex:].find('&amp')
							name = s_row[begindex+len('pid='):begindex+endex]
							ta_names.append(name)
						if len(ta_names)==0:
							continue
						ta_vote_info = [yr, mo, day, day_ticker, subject, result, 'TA']
						print 'ta_vote_info: %s' %(ta_vote_info)
						ta_vote_info.extend(ta_names)
						print 'ta_names: %s' %(ta_names)
						print 'before writing ta row'
						c_writer.writerow(ta_vote_info)
						print 'after writing ta row'
						nil_names = []
						for row in nil_vote_tds:
							#s_row = str(row)
							s_row = row.encode()
							begindex = s_row.find('pid=')
							if begindex==-1:
								continue
							endex = s_row[begindex:].find('&amp')
							name = s_row[begindex+len('pid='):begindex+endex]
							nil_names.append(name)
						if len(nil_names)==0:
							continue
						nil_vote_info = [yr, mo, day, day_ticker, subject, result, 'NIL']
						nil_vote_info.extend(nil_names)
						print 'before writing nil row'
						c_writer.writerow(nil_vote_info)
						print 'day ticker: %s' %(day_ticker)
						print 'result: %s'%(result)
						day_ticker+=1
					except:
						print 'ERROR: %s%s%s #%s' %(yr,mo,day,day_ticker)
						pass

c.flush()
c.close()
