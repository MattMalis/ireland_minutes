#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup as BS
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

c1 = open('seanad_sep12-cur_votes.csv', 'wb')
c_writer = csv.writer(c1)
c_writer.writerow(["Year", "Month", "Day", "Vote #", "Subject", "Result","Ta/Nil","Legislators"])
#c_writer.writerow(["Year", "Month", "Day", "Vote #", "Subject","Ta/Nil","Legislators"])

cc = open('seanad_sep12-cur_nonRC.csv','wb')
cc_writer = csv.writer(cc)#, encoding = 'utf-8')
cc_writer.writerow(["Year", "Month", "Day", "Subject", "Non-RCV Result"])

for yr in range(2012,2017): ## newest web format runs from sep2012 through present
	this_yr_months = os.listdir(base_path+str(yr))
	for mo in this_yr_months: 
		if mo == '.DS_Store':
			continue
		if yr==2012:
			if mo not in ['September', 'October', 'November', 'December']:
				continue
		this_months_days = os.listdir(base_path+str(yr)+'/'+mo)
		for day in this_months_days:
			#print '\n TODAY: %s%s%s' %(yr,mo,day)
			if day == '.DS_Store': # sometimes os.listdir() returns '.DS_Store' as the 0th item in the list
				continue
			day_ticker = -1
			day_file_names = import_one_day_htmls(yr, mo, day)	## all the html files from a single day	
			for f_name in day_file_names:
				one_file_vote_tables = [] 
				page = open(base_path+str(yr)+'/'+mo+'/'+day+'/'+f_name)
				soup = BS(page.read(), 'html.parser')
				## looking for subject in the <title> tag
				titles = soup.find_all('title')
				#str_title = str(title) #str() was causing encoding problems...
				subject = ''
				if len(titles)>0: 
					t_txt = titles[0].get_text()
					#print 't_txt: %s' %(t_txt)
					## title tages take format: 'Seanad Eireann - DD/Mon/YYYY Subject Matter (Continued), eg
					begindex = t_txt.find(' - ') + len(' - ')
					#endex = t_txt[begindex:].find('</title>')
					if begindex!=-1:# and endex!=-1:
						subject = t_txt[begindex:]#begindex+endex]
						#print 'date: %s, %s, %s; subject: %s' %(yr,mo,day,subject)					
				## results of votes - always found in <p> tag with 'class="pcentre"' attribute
				all_p_center = soup.find_all('p',{'class':['pcentre']})
				results = []
				for p in all_p_center:
					#pt = p.get_text()
					pt = ''.join([letr for letr in p.get_text() if ord(letr)<128])
					## don't want to catch long blocks of speeches that happen to include "declared"
					## (100 char cutoff is arbitrary...)
					if len(pt)<100:
						if 'amendment' in pt.lower() or 'question' in pt.lower() or 'declared' in pt.lower():
							results.append(pt)
				if len(results)>1:
					print "len(results)>1 for day: %s, %s, %s" %(yr, mo, day)
				## now, finding the results for non-RC votes:
				all_p = soup.find_all('p')
				## looking at the <p> tags that do not have the attributes described above
				p_not_center = [p for p in all_p if p not in all_p_center]
				for p in p_not_center:
					pt = ''.join([c for c in p.get_text() if ord(c)<128])
					if len(pt)<100:
						if 'carried' in pt.lower() or 'agreed' in pt.lower() or 'declared' in pt.lower():
								try:
									#print type(pt)
									cc_writer.writerow([yr,mo,day,subject,pt])
								except:
									print "couldn't write non-RC vote record to csv, date: %s%s%s\n" %(yr,mo,day)
									print pt
									pass
				tables = soup.find_all('table')
				for t in range(len(tables)):
					if len(tables[t].find_all('table'))!=0:
						#print 'table in a table! day: %s%s%s' %(yr,mo,day)
						one_file_vote_tables.extend(tables[t].find_all('table'))
				for i in range(0,len(one_file_vote_tables)):
					try:
						print '\n\n'
						day_ticker+=1
						vt = one_file_vote_tables[i]
						ta_vote_tds = vt.find_all('td',{'bgcolor':'#ccffcc'}) 
						nil_vote_tds = vt.find_all('td',{'bgcolor':'#ffcccc'})			
						ta_names = []
						for row in ta_vote_tds:
							s_row = str(row)
							begindex = s_row.find('pid=')
							if begindex==-1:
								continue
							endex = s_row[begindex:].find('&amp')
							name = s_row[begindex+len('pid='):begindex+endex]
							ta_names.append(name)
						if len(ta_names)==0:
							continue
						ta_vote_info = [yr, mo, day, day_ticker, subject, results[0], 'TA']
						ta_vote_info.extend(ta_names)
						c_writer.writerow(ta_vote_info)
						nil_names = []
						for row in nil_vote_tds:
							s_row = row.encode()
							begindex = s_row.find('pid=')
							if begindex==-1:
								continue
							endex = s_row[begindex:].find('&amp')
							name = s_row[begindex+len('pid='):begindex+endex]
							nil_names.append(name)
						if len(nil_names)==0:
							continue
						nil_vote_info = [yr, mo, day, day_ticker, subject, results[0], 'NIL']
						nil_vote_info.extend(nil_names)
						c_writer.writerow(nil_vote_info)
					except:
						print 'ERROR: %s%s%s #%s' %(yr,mo,day,day_ticker)
						pass

c1.flush()
c1.close()
cc.flush()
cc.close()