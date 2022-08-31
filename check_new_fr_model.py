#http://feynrules.irmp.ucl.ac.be/timeline?from=Apr+1%2C+2018&daysback=30&authors=&wiki=on&update=Update

import urllib.request, urllib.parse, urllib.error
import sys
import datetime
from datetime import date
import re

import check_database

today = date.today()
last_check = eval(open("last_fr_check").read())
print(last_check)

delta = today - last_check
if (delta.days>90):
    print("WARNING maximum time stamp is 90 days")
    today = last_check + datetime.timedelta(days=90)
    print(today)



this_year = today.year
months = {1:'Jan', 2:'Feb', 3: "Mar", 4:"Apr", 5:"May",6:"Jun", 7:"Jul", 8: "Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
this_month = today.month
this_day = today.day
print((this_year, this_month, this_day))

print(("http://feynrules.irmp.ucl.ac.be/timeline?from=%s+%s%%2C+%s&daysback=%s&authors=&wiki=on&update=Update" % (this_month, this_day, this_year, delta.days)))
data = urllib.request.urlopen("http://feynrules.irmp.ucl.ac.be/timeline?from=%s+%s%%2C+%s&daysback=%s&authors=&wiki=on&update=Update" % (this_month, this_day, this_year, delta.days))

import re
#pattern = '''\<dt class="attachment"\>'''
pattern='''<a href="/attachment/wiki/(?P<link>[/\w.]*)">'''
pattern='''<a\s*href="/attachment/wiki/(?P<link>[/\w.\-_]*)"
                .*? 
               by\s*<span\s+class="author">(?P<author>[\w\s.]*)</span>
'''

pattern = re.compile(pattern, re.I+re.M+re.X+re.DOTALL)

text = data.read()

current_db = {}
invert_db = {}

base_db = open("model_database.dat","a")
text = text.decode()
print((text.count('''href="/attachment/wiki/''')))
for match in pattern.finditer(text):
    link, author = match.groups()
    if not link.endswith(('.tar.gz','.gz','.zip','.tgz','.tar')):
        continue
    print(("found new attachment: %s by %s" % (link, author)))
    link= "http://feynrules.irmp.ucl.ac.be/raw-attachment/wiki/"+link
    
    if link in invert_db:
        print(("        update of old link for model %s " % invert_db[link]))
        continue
    modelname = check_database.validate_UFO_link(link)
    if not modelname:
        print("        Not valid UFO model")
    elif modelname in current_db:
        print(("        found modelname %s duplicate with existing model: %s" % (modelname,current_db[modelname])))
        ans = eval(input("Do you want to update the database (y/n)"))
        if ans == "y":
            base_db.write("%s %s\n" % (modelname, link))
    else:
        print(("        NEW model: %s" % modelname))
        ans = input("Do you want to add it to the database (y/n)")
        if ans == "y":
            base_db.write("%s %s\n" % (modelname, link))
        
        
#print pattern.findall(text)
#print len(pattern.findall(text))


if True:
    f = open("last_fr_check", "w")
    f.write(repr(today))
    f.close()
