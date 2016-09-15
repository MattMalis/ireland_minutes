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

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December'] 

## creating column headers for each legislator; looks like there won't be more than 55 for any single vote
legis_names = []
for i in range(55):
	next_legis_name = "Legislator%s"%(i)
	legis_names.append(next_legis_name)

c1 = open('seanad_30-03_votes_orig.csv', 'wb')

c_writer = csv.writer(c1, encoding = 'utf-8')
colnames = ["Year", "Month", "Day", "Vote_Num", "File_Name","Subject", "Result","Ta/Nil","Tally"]
colnames.extend(legis_names)
c_writer.writerow(colnames)

cc = open('seanad_30-03_nonRC_orig.csv','wb')
cc_writer = csv.writer(cc, encoding = 'utf-8')
cc_writer.writerow(["Year", "Month", "Day", "File_Name","Subject", "Non-RCV Result"])


####### FUNCTION DEFINITIONS ###########

## return only ascii characters; replace non-ascii chars with '_'
def ascii_only(original_string):
	try:
		letrs = []
		for letr in original_string:
			if ord(letr)<128:
				letrs.append(letr)
			else:
				letrs.append('_')
		return ''.join(letrs)
	except:
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
	
## determine whether a vote table lists ta or nil votes		
def ta_or_nil(vote_table):
	cur = vote_table.previousSibling
	count = 0
	while (True):
		if count>3 or cur==None:
			return 'NOT A VOTE TABLE' ## when this function is called, if it returns 'NOT A VOTE TABLE',
				## we assume the table was mischaracterized as a vote table, and move on to next table
		if cur.name==None:
			count+=1
			cur = cur.previousSibling
		elif cur.name=='p' and len(cur.get_text())<50: ## 50 chars is arbitrary
			if 'T_' in ascii_only(cur.get_text()):	
				return 'TA'
			if 'N_l' in ascii_only(cur.get_text()):
				return 'NIL'
			cur = cur.previousSibling
			count +=1
		else:
			cur = cur.previousSibling
			count +=1
		
## extract legislator names from a vote table	
def get_legislator_names(vote_table):
	tds = vote_table.find_all('td')
	legislator_names = []
	for td in tds:
		names = [ascii_only(x) for x in list(td.children) if ascii_only(x)!='']
		legislator_names.extend(names)
	return legislator_names

## some files have their result statement in a <td> tag, instead of a <p> tag...
def catch_result_tds(file_soup):
	all_tds = file_soup.find_all('td')
	keywords = ['amendment', 'motion','question','declared', 'ordered']
	result_tds = []
	for td in all_tds:
		## 200 chars is arbitrary
		if len(td.get_text())<200 and any(k in td.get_text().lower() for k in keywords):
			result_tds.append(td)
	return result_tds
			
## find the Result statment for an RC vote immediately following a vote table
def get_one_RC_result(vote_table):
	keywords = ['amendment', 'motion','question','declared', 'ordered']
	cur = vote_table.nextSibling
	count = 0
	while(True):
		try:
			if count >20: ## some files have a few lines of speech before the vote result is listed; 20 nextSibling's is arbirtrary
				return ''
			if cur is None:
				return ''
			if cur.name==None:
				count+=1
				cur = cur.nextSibling
				continue
			elif cur.name=='p' and len(cur.get_text())<200:
				if any(k in cur.get_text().lower() for k in keywords):
					return ascii_only(cur.get_text())
				else:
					count+=1
					cur = cur.nextSibling
					continue
			count +=1
			cur = cur.nextSibling
		except:
			if cur is None:
				return ''
			cur = cur.nextSibling
### I don't have this working to find a result statement in a <td> tag.
## 		See 'Ireland-seanad-minutes-2001March28-p7.html' for example.	



########## DOING THE WORK ########
for yr in range(1930,2004):## all files 1930-2004 appear to share same format
	if yr==1937:## no minutes found online for 1937
		continue
	this_yr_months = os.listdir(base_path+str(yr))
	for mo in this_yr_months: 
		if mo not in months:
			continue
		if mo == '.DS_Store': # sometimes os.listdir() returns '.DS_Store' as the 0th item in the list...
			continue
		this_months_days = os.listdir(base_path+str(yr)+'/'+mo)
		## this_months_days is a list of folder names, corresponding to days within a given month for which there are legislative minutes
		for day in this_months_days:
			if day == '.DS_Store': 
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
				try:
					this_file_result_tds = catch_result_tds(soup)
				except:
					print "failed to catch result_tds for file: %s" %(f_name)
					this_file_result_tds = []

				
				## EXTRACTING LEGISLATOR VOTES AND WRITING TO CSV
				for i in range(len(vote_tables)):
					try:
						
						##workaround for the fact that some tables are split... (eg 'ta' and 'ta,continued')
						try:
							outcome = ta_or_nil(vote_tables[i])
						except:
							print 'failed to get outcome for table # %s for file: %s' %(i, f_name)
							outcome==None
							
						if outcome=='NOT A VOTE TABLE': ## it wasn't actually a vote table
							continue ## move on to next vote table
						
						try:			
							names = get_legislator_names(vote_tables[i]) ## function defined above
						except:
							print 'failed to get legislator names for table # %s for file: %s' %(i, f_name)
							names=[]
						
						
						next_outcome = '...'
						if i+1<len(vote_tables): ## if the current vote table is not the last one in the list
							next_outcome = ta_or_nil(vote_tables[i+1]) ## check the next outcome (ta or nil)
						
						if outcome==next_outcome: #if there are two nil or two ta tables back-to-back
							print 'hit a continued table in file: %s'%(f_name)	
							# (ie if the second one is 'continued')... this does not seem to be substantively meaningful, just a formatting thing
							names.extend(get_legislator_names(vote_tables[i+1]))
							i+=1 ## increment vote tables in the for loop 
							## (don't want to treat back-to-back 'ta' tables like they're two separate votes)
							## use the second table to find the result statement (below)								
						
						try:
							res = get_one_RC_result(vote_tables[i]) ## function defined above
							## get_one_RC_result returns '' if it cannot find a result statement
						except:
							print 'failed to get RC result for table # %s for file: %s' %(i, f_name)
							res = ''
	
						
						if outcome=='NIL' and outcome!=next_outcome: ## if this is the last nil table before a ta table
						## it should be followed by a result statement
							if res=='':
								print "WARNING: did not find result for table#%s from file: %s" %(i,f_name)
						
						## storing RC results in a list, to refer to later when extracting non-RC results
						## 		
						if res!='':
							this_file_RC_results.append(res)
						

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
				## NOTE: this is faulty - eg. "Question declared carried" can exist in the file both as an RC result and
				## 		a non-RC result; but if it does, it will be added to the RC results list, and the non-RC 
				## 		instance of it will not be added to the non-RC list... (no way to tell it's not the same one)	
				
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