
import urllib2
import datetime
import time
import random
import os
import csv
import re
from bs4 import BeautifulSoup

base_path = '/Users/iramalis/Desktop/ireland-seanad-minutes/'

def import_one_day_htmls(yr, mo, day):
	try:
		day_folder = base_path+'%s/%s/%s'%(yr, mo, day)
		file_names = os.listdir(day_folder)
		return file_names
	except:
		print 'ERROR in import_one_day_htmls(%s, %s, %s)'%(yr,mo,day)
		pass


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December'] 

c = open('sep12-cur_votes.csv', 'wb')
c_writer = csv.writer(c)
c_writer.writerow(["Year", "Month", "Day", "Vote #", "Ta/Nil","Legislators"])

for yr in range(2012,2017):
	this_yr_months = os.listdir(base_path+str(yr))
	for mo in this_yr_months[1:]:
		if yr==2012:
			if mo not in ['September', 'October', 'November', 'December']:
				continue
		this_months_days = os.listdir(base_path+str(yr)+'/'+mo)
		for day in this_months_days[1:]:
			print '\n\n TODAY: %s%s%s' %(yr,mo,day)
			day_file_names = import_one_day_htmls(yr, mo, day)
			one_day_vote_tables = []
			for f_name in day_file_names:
				page = open(base_path+str(yr)+'/'+mo+'/'+day+'/'+f_name)
				soup = BeautifulSoup(page.read(), 'html.parser')
				tables = soup.find_all('table')
				for t in range(len(tables)):
					if len(tables[t].find_all('table'))!=0:
						one_day_vote_tables.extend(tables[t].find_all('table'))
				for i in range(len(one_day_vote_tables)):
					try:
						#print 'Vote table #%s: length=%s'%(i,len(one_day_vote_tables[i]))
						vt = one_day_vote_tables[i]
						ta_vote_tds = vt.find_all('td',{'bgcolor':'#ccffcc'}) 
						nil_vote_tds = vt.find_all('td',{'bgcolor':'#ffcccc'})			
						#print '\n TA VOTES:'
						ta_names = []
						for row in ta_vote_tds:
							s_row = str(row)
							begindex = s_row.find('pid=')
							if begindex==-1:
								continue
							endex = s_row[begindex:].find('&amp')
							name = s_row[begindex+len('pid='):begindex+endex]
							#print name
							ta_names.append(name)
						#print '\n\n NIL VOTES:'
						c_writer.writerow([yr, mo, day, i, 'TA']+ta_names)
						nil_names = []
						for row in nil_vote_tds:
							s_row = str(row)
							begindex = s_row.find('pid=')
							if begindex==-1:
								continue
							endex = s_row[begindex:].find('&amp')
							name = s_row[begindex+len('pid='):begindex+endex]
							#print name
							nil_names.append(name)
						c_writer.writerow([yr, mo, day, i,'NIL']+ta_names)
					except:
						print 'ERROR: %s%s%s #%s' %(yr,mo,day,i)

c.flush()
c.close()
