import urllib2
import datetime
import time
import random
import os
import csv
from bs4 import BeautifulSoup

seanad_base_address = 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=seanad&year='
seanad_year_addresses = []


# 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/seanad' + 'YYYYMMDD' + '000' + ['01' through end (eg '56')]
# bottom right, on main page for specific date - 'page 1 of __' (50, 56, eg)
# '01' is the main page for date; '02' is prelude, etc...

# looks like every vote starts with: 'The Seanad divided'

# number of pages: '</select> of XX' --dropdown menu, XX will be the last page -- these are the only </select> tags on the page
