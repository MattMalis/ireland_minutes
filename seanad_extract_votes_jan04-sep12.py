#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import urllib2
import datetime
import time
import random
import os
#import csv
import unicodecsv as csv
import re
from bs4 import BeautifulSoup as BS
import codecs

### Run this script after all legislative minutes have already been downloaded,
##		and are stored as html files in directories of the form 
##			/Desktop/ireland-seanad-minutes/YYYY/MonthName/DD

print '\n\n\n\n\n\n\n\n'


base_path = '/Users/iramalis/Desktop/ireland-seanad-minutes/'

def one_day_html_filenames(yr, mo, day):
	try:
		if not isinstance(day,str):
			day = str(day)
		if len(day)==1:
			day = '0'+day
		day_folder = base_path+'%s/%s/%s'%(yr, mo, day)
		file_names = os.listdir(day_folder)
		return file_names
	except:
		print 'ERROR in one_day_html_filenames(%s, %s, %s)'%(yr,mo,day)
		pass


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December'] 

c1 = open('seanad_jan04-sep12_votes_orig.csv', 'wb')
c_writer = csv.writer(c1, encoding = 'utf-8')
c_writer.writerow(["Year", "Month", "Day", "Vote_Num", "File_Name","Subject", "Result","Ta/Nil","Tally","Legislators"])
#c_writer.writerow(["Year", "Month", "Day", "Vote #", "Subject","Ta/Nil","Legislators"])

cc = open('seanad_jan04-sep12_nonRC_orig.csv','wb')
cc_writer = csv.writer(cc, encoding = 'utf-8')
cc_writer.writerow(["Year", "Month", "Day", "File_Name","Subject", "Non-RCV Result"])


####### FUNCTION DEFINITIONS ###########

def ascii_only(original_string):
	return ''.join([ltr for ltr in original_string if ord(ltr)<128])
	
def get_subject(file_soup):
## looking for subject in the <title> tag
	titles = file_soup.find_all('title')
	subj = ''
	if len(titles)>0: 
		t_txt = titles[0].get_text()
		## title tages take format: 'Seanad Eireann - DD/Mon/YYYY Subject Matter (Continued), eg
		## accent on the Eireann causes encoding problems - skip that
		begindex = t_txt.find(' - ') + len(' - ')
		if begindex!=-1:
			subj = t_txt[begindex:]
	return subj

def get_one_RC_result(red_table):
	keywords = ['amendment', 'question','declared']
	cur = red_table.nextSibling
	while(True):
		try:
			if cur.name=='table':
				return ''
			if cur.name=='p':
				for k in keywords:
					if k in cur.get_text().lower():
						return ascii_only(cur.get_text())
			cur = cur.nextSibling
		except:
			cur = cur.nextSibling
				
	
def get_RC_results(center_p_all):
	## results of RC votes - always found in <p> tag with 'class="pcentre"' attribute
	rc_results = []
	for p in center_p_all:
		pt = ascii_only(p.get_text())
		## don't want to catch long blocks of speeches that happen to include the keywords below
		## (100 char cutoff is arbitrary...)
		if len(pt)<100:
			if 'amendment' in pt.lower() or 'question' in pt.lower() or 'declared' in pt.lower():
				rc_results.append(pt)
	return rc_results			

def legislator_names_from_table(vote_table):
	legislator_names = []
	bad_td = vote_table.find_all('td',{'colspan':'2'})
	all_td = vote_table.find_all('td')
	good_td = [t for t in all_td if t not in bad_td]
	for row in good_td:
		s_row = str(row)
		## each entry in the vote table includes a name and a link to more info on the legislator
		##		the names sometimes have non-ascii characters, but the links are always ascii
		##		in the links, names are found between "pid=" and "&amp"
		## (note - for side with fewer votes, there will be blank entries at the end of the column)
		begindex = s_row.find('pid=')
		if begindex==-1:
			## this most likely means we hit a blank row
			continue
		endex = s_row[begindex:].find('&amp')
		name = s_row[begindex+len('pid='):begindex+endex]
		legislator_names.append(name)
	return legislator_names
	
	
	

########## DOING THE WORK ########

#for yr in range(2004,2013): ## 2nd newest format: seems to be Jan2004 through July 2012
for yr in range(2004,2005):
	this_yr_months = os.listdir(base_path+str(yr))
	for mo in ['January','February']:#this_yr_months: 
		if mo == '.DS_Store':
			continue
		if yr==2012: ## months in 2012 after September follow the newest format
			if mo in ['September', 'October', 'November', 'December']:
				continue
		this_months_days = os.listdir(base_path+str(yr)+'/'+mo)
		## this_months_days is a list of folder names, corresponding to days within a given month for which there are legislative minutes
		for day in this_months_days:
			if day == '.DS_Store': # sometimes os.listdir() returns '.DS_Store' as the 0th item in the list
				continue
			day_ticker = -1
			day_file_names = one_day_html_filenames(yr, mo, day)	## all the html filenames from a single day	
			for f_name in day_file_names:
				page = open(base_path+str(yr)+'/'+mo+'/'+day+'/'+f_name)
				soup = BS(page.read(), 'html.parser')
				try: ## EXTRACTING VOTE SUBJECT
					subject = get_subject(soup) ## function defined above
				except:
					print 'ERROR: could not extract vote subject for file: %s' %(f_name)
					subject = ''
					pass
				# all_p_center = soup.find_all('p',{'class':['pcentre']})
# 				try: ## EXTRACTING RC VOTE RESULTS
# 					file_RC_results = get_RC_results(all_p_center)## function defined above
# 				except:
# 					print 'ERROR: could not extract RC vote results for file: %s' %(f_name)
# 					pass
				## EXTRACTING NON-RC VOTE RESULTS AND WRITING TO CSV
				##		(easier to do this without creating a function...)
				# all_p = soup.find_all('p')
# 				## looking at the <p> tags that do not have the attributes described above
# 				p_not_center = [p for p in all_p if p not in all_p_center]
# 				for p in p_not_center:
# 					pt = ''.join([c for c in p.get_text() if ord(c)<128])
# 					if len(pt)<100:
# 						if 'carried' in pt.lower() or 'agreed' in pt.lower() or 'declared' in pt.lower():
# 								try:
# 									cc_writer.writerow([yr,mo,day,f_name,subject,pt])
# 								except:
# 									print "NON-RC ERROR: fail to record to csv from filename: %s" %(f_name)
# 									print pt
# 									pass
				#try: ## EXTRACTING VOTE TABLES
			#		one_file_vote_tables = get_one_file_vote_tables(soup) ## function defined above
			#	except: 
					## might not actually be an error - might just be that there was a table that wasn't a vote table
					##		but that happened to have one of the keywords above it
			#		print "WARNING: failed to extract vote table from file: %s" %(f_name)
			#		pass
			
			
				green_tables = soup.find_all('table', {'bgcolor': '#CCFFCC'})
				red_tables = soup.find_all('table', {'bgcolor': '#FFCCCC'})
				if len(green_tables)!=len(red_tables):
					print "ERROR: unequal number of green tables and red tables for file: %s" %(f_name)
					continue
					
				## EXTRACTING LEGISLATOR VOTES AND WRITING TO CSV
				for i in range(len(green_tables)):
					try:
						day_ticker+=1
						## length of file_RC_results should be same as length of one_file_vote_tables
						## 		(one vote result listed below each vote table)
						## 		if it's not, something went wrong
						# if len(file_RC_results)<=i:
# 							if len(file_RC_results)==0:
# 								res = ['']
# 							else:
# 								res = file_RC_results[-1]
# 							print 'WARNING: file_RC_results shorter than one_file_vote_tables for filname: %s' %(f_name)
# 						else: ## this one is what we want
# 							res = file_RC_results[i]
						#vt = one_file_vote_tables[i]
						
						## table entries for ta and nil votes can be identified by background color
						## each legislator has her own <td> tag
						
						#ta_vote_tds = vt.find_all('td',{'bgcolor':'#ccffcc'}) 
						#nil_vote_tds = vt.find_all('td',{'bgcolor':'#ffcccc'})										
						res = ''
						res = get_one_RC_result(red_tables[i])
						print res
						if res=='':
							print "WARNING: did not find result for table#%s from file: %s" %(i,f_name)
						ta_names = legislator_names_from_table(green_tables[i]) ## function defined above
						nil_names = legislator_names_from_table(red_tables[i])
											
						## COLLECT INFO AND WRITE TO CSV
						ta_vote_info = [yr, mo, day, day_ticker, f_name,subject, res, 'TA',len(ta_names)]
						ta_vote_info.extend(ta_names)
						c_writer.writerow(ta_vote_info)
						
						nil_vote_info = [yr, mo, day, day_ticker, f_name,subject, res, 'NIL',len(nil_names)]
						nil_vote_info.extend(nil_names)
						c_writer.writerow(nil_vote_info)
					except:
						#print 'ERROR: %s%s%s #%s' %(yr,mo,day,day_ticker)
						print 'ERROR: writing csv for table#%s from file: %s' %(i, f_name)
						pass

c1.flush()
c1.close()
cc.flush()
cc.close()