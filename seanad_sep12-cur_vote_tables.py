
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

nov07_12 = import_one_day_htmls(2012, 'November', '07')

one_day_vote_tables = []
for f_name in nov07_12:
	page = open(base_path+'2012/November/07/'+f_name)
	soup = BeautifulSoup(page.read(), 'html.parser')
	tables = soup.find_all('table')
	table_strings = {}
	table_soups = {}
	for t in range(len(tables)):
		if len(tables[t].find_all('table'))!=0:
			one_day_vote_tables.extend(tables[t].find_all('table'))

			
			
## name = re.findall(r'\s\s\w*,\s\w*\.\s\s',str(tas[0]))
## better:
# >>> for row in ta_vote_tds:
# ...     s_row = str(row)
# ...     name = re.findall(r'\s\s\w.*,\s\w.*\.\s\s',s_row)
# ...     print name

vt = one_day_vote_tables[0]
ta_vote_tds = vt.find_all('td',{'bgcolor':'#ccffcc'}) 
nil_vote_tds = vt.find_all('td',{'bgcolor':'#ffcccc'})

for row in nil_vote_tds:
	s_row = str(row)
	#print funky_string
	#s_row = ''
	#for c in funky_string: #s_row = ''.join([x if ord(x) < 128 else '?' for x in funky_string])
	#		if ord(c) <128:
	#		s_row += c
	#print s_row
	#print '\n\n'
	#name = re.findall(r'\s\s\w.*,\s\w.*\.\s\s',s_row)
	begindex = s_row.find('pid=')
	if begindex==-1:
		continue
	endex = s_row[begindex:].find('&amp')
	name = s_row[begindex+len('pid='):begindex+endex]
	print name
### great, except wtf to do about non-ascii characters (accented vowels...)

## 'pid=FirstLast&amp'
