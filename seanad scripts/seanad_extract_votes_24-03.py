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

### Got one error message from running this script:
## "ERROR: writing csv for table#0 from file: Ireland-seanad-minutes-2008April30-p8.html"



### Run this script after all legislative minutes have already been downloaded,
##		and are stored as html files in directories of the form 
##			/Desktop/ireland-seanad-minutes/YYYY/MonthName/DD

print '\n\n\n\n\n\n'


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

#months = ['March', 'September']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December'] 


legis_names = []
for i in range(55):
	next_legis_name = "Legislator%s"%(i)
	legis_names.append(next_legis_name)

c1 = open('seanad_24-03_votes_orig.csv', 'wb')

c_writer = csv.writer(c1, encoding = 'utf-8')
colnames = ["Year", "Month", "Day", "Vote_Num", "File_Name","Subject", "Result","Ta/Nil","Tally"]
colnames.extend(legis_names)
c_writer.writerow(colnames)

cc = open('seanad_24-03_nonRC_orig.csv','wb')
cc_writer = csv.writer(cc, encoding = 'utf-8')
cc_writer.writerow(["Year", "Month", "Day", "File_Name","Subject", "Non-RCV Result"])


####### FUNCTION DEFINITIONS ###########

def ascii_only(original_string):
	try:
		letrs = []
		for letr in original_string:
			if ord(letr)<128:
				letrs.append(letr)
			else:
				letrs.append('_')
		return ''.join(letrs)
		#return ''.join([ltr for ltr in original_string if ord(ltr)<128])
	except:
		#print 'unable to ascii-fy %s'%(original_string)
		return ''
	
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
	return ascii_only(subj)


def find_vote_tables(file_soup):
	all_tables = file_soup.find_all('table')
	vote_tables = [t for t in all_tables if len(t.find_all('colgroup'))!=0 and len(t.find_all('table'))==0]
	## some files are formatted with an outer table that contains a large part of the table's contents...
	## 		(want to skip those tables)
	return vote_tables
# 
# for i in range(len(vt1)):
# 	print 'starting on table #%s'%(i)
# 	outcome = ta_or_nil(vt1[i])
# 	if outcome=='NONE':
# 		continue
# 	else:
# 		print vt1[i]
	
def ta_or_nil(vote_table):
	cur = vote_table.previousSibling
	count = 0
	while (True):
		#print 'count: %s' %(count)
		#print 'cur: %s \n\n' %(cur)
		if count>3 or cur==None:
			return 'NONE'
		if cur.name==None:
			#print 'name for %s is none' %(count)
			count+=1
			cur = cur.previousSibling
		elif cur.name=='p' and len(cur.get_text())<100:
			if 'T_' in ascii_only(cur.get_text()):	
				#print 'got a ta!'
				return 'TA'
			if 'N_l' in ascii_only(cur.get_text()):
				#print 'got a nil!'
				return 'NIL'
			cur = cur.previousSibling
			count +=1
		else:
			#print 'else'
			cur = cur.previousSibling
			count +=1
		

	
def get_legislator_names(vote_table):
	tds = vote_table.find_all('td')
	legislator_names = []
	for td in tds:
		names = [ascii_only(x) for x in list(td.children) if ascii_only(x)!='']
		legislator_names.extend(names)
	return legislator_names

def get_one_RC_result(vote_table):
	keywords = ['amendment', 'motion','question','declared', 'ordered']
	cur = vote_table.nextSibling
	count = 0
	while(True):
		try:
			#print 'count: %s' %(count)
			if count >10:
				return ''
			if cur is None:
				return ''
			if cur.name==None:
				count+=1
				cur = cur.nextSibling
 			elif cur.name=='table': 
 				## moving through siblings, if you hit a table before a result <p>, that means you started with a ta table
 				## 		(or with a nil table before a [nil, continued] table)
 				return ''
			elif cur.name=='p' and len(cur.get_text())<100:
				if any(k in cur.get_text().lower() for k in keywords):
					return ascii_only(cur.get_text())
				else:
					count+=1
					cur = cur.nextSibling
			else:
				#print 'cur.name: %s' %(cur.name)
				count +=1
				cur = cur.nextSibling
		except:
			if cur is None:
				return ''
			cur = cur.nextSibling



########## DOING THE WORK ########
for yr in range(1930,2004):
#for yr in range(1924,2004): ## all files 1924-2004 appear to share same format
#for yr in range(2003,2004):
	if yr==1937:## no minutes found online for 1937
		continue
	this_yr_months = os.listdir(base_path+str(yr))
	for mo in this_yr_months: 
		if mo not in months:
			continue
		if mo == '.DS_Store':
			continue
		this_months_days = os.listdir(base_path+str(yr)+'/'+mo)
		## this_months_days is a list of folder names, corresponding to days within a given month for which there are legislative minutes
		for day in this_months_days:
			if day == '.DS_Store': # sometimes os.listdir() returns '.DS_Store' as the 0th item in the list
				continue
			day_ticker = 0
			day_file_names = one_day_html_filenames(yr, mo, day)	## all the html filenames from a single day	
		###### F_NAME LOOP	
			for f_name in day_file_names:
				#print 'beginning file: %s' %(f_name)
				try:
					page = open(base_path+str(yr)+'/'+mo+'/'+day+'/'+f_name)
					soup = BS(page.read(), 'html.parser')
				except:
					print 'failed to make soup out of file: %s' %(f_name)
					pass
				try: ## EXTRACTING VOTE SUBJECT
					subject = get_subject(soup) ## function defined above
				except:
					print 'ERROR: could not extract vote subject for file: %s' %(f_name)
					subject = ''
					pass
				try:
					vote_tables = find_vote_tables(soup)
				except:
					print 'failed to find vote tables for file: %s' %(f_name)
					pass
				
				this_file_RC_results = []	
				
				## EXTRACTING LEGISLATOR VOTES AND WRITING TO CSV
				for i in range(len(vote_tables)):
					try:
						
						##workaround for the fact that some tables are split... (eg 'ta' and 'ta,continued')
						outcome = ta_or_nil(vote_tables[i])
						if outcome=='NONE': ## it wasn't actually a vote table
							continue
							
						next_outcome = '...'
						if i+1<len(vote_tables):
							next_outcome = ta_or_nil(vote_tables[i+1])
							
						names = get_legislator_names(vote_tables[i]) ## function defined above
						#print 'names for file %s: \n %s' %(f_name, names)					
						res = get_one_RC_result(vote_tables[i]) ## function defined above
							## get_one_RC_result returns '' if it hits another table before it finds a result
						#print 'res:   %s   for file:  %s' %(res,f_name)

						if outcome==next_outcome: #if there are two nil or two ta tables back-to-back
							print 'hit a continued table in file: %s'%(f_name)	
							# (ie if the second one is 'continued')
							names.extend(get_legislator_names(vote_tables[i+1]))
							i+=1 ## double-increment in the for loop 								

						
						if outcome=='NIL' and outcome!=next_outcome: ## if this is the last nil table before a ta table
							if res=='':
								print "WARNING: did not find result for table#%s from file: %s" %(i,f_name)
						
						## storing RC results in a list, to refer to later when extracting non-RC results
						## 		
						if res!='':
							this_file_RC_results.append(res)
						## NOTE: this is faulty - "Question declared carried" can exist in the file both as an RC result and
						## 		a non-RC result; but if it does, it will be added to the RC results list, and the non-RC 
						## 		instance of it will not be added to the non-RC list... (no way to tell it's not the same one)						
						j=i
						## if this vote table does not immediate precede a result, 
						##		scan forward until you find a result, and make it this vote table's result
						while (res==''):
							if j>=len(vote_tables):
								break
							res = get_one_RC_result(vote_tables[j])
							j+=1
						
						names = [n for n in names if n!='' and n!='_']
						
					
						## COLLECT INFO AND WRITE TO CSV
						csv_row_info = [yr, mo, day, day_ticker, f_name,subject, res, outcome,len(names)]
						csv_row_info.extend(names)
						c_writer.writerow(csv_row_info)
						
						
						day_ticker+=1

					except:
						print 'ERROR: writing csv for table#%s from file: %s' %(i, f_name)
						pass
				
				## All non-RC vote results seem to be listed in short <p> tags
				## RC results have been stored in this_file_RC_results
				## finding all the <p> tags that meet certain criteria (below),
				## 		that are not found in this_file_RC_results
				try:
					all_p = soup.find_all('p')
					all_p_not_RC = [p for p in all_p if p not in this_file_RC_results]
				except:
					print 'could not identify all_p_not_RC for file: %s' %(f_name)
					pass
				nonRC_results = []
				for p in all_p_not_RC:
					try:
						pt = ascii_only(p.get_text())
						keywords = ['amendment','question','motion','declared','agreed']
						if len(pt)<100:
							if any(k in pt.lower() for k in keywords):
								nonRC_results.append(pt)
					except:
						print 'ERROR extracting nonRC_results for file: %s' %(f_name)
						pass
				## writing each of the stored non-RC results to its own line in the non-RC csv file
				for r in nonRC_results:
					try:
						cc_writer.writerow([yr,mo,day,f_name,subject,r])
					except:
						print 'ERROR writing nonRC to csv for file: %s' %(f_name)
						pass			
				
				

c1.flush()
c1.close()
cc.flush()
cc.close()