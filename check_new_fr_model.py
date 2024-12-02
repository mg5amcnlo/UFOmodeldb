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




def get_modeldatabase():
    current_db = {}
    invert_db = {}
    for line in open("model_database.dat"):
        name, link = line.split(None, 1)
        invert_db[link] = name
        current_db[name] = link
    current_db['loop_sm'] = 'internal-to-mg'
    current_db['sm'] = 'internal-to-mg'
    current_db['taudecay_UFO'] = 'internal-to-mg'
    current_db['hgg_plugin'] = 'internal-to-mg'
    current_db['MSSM_SLHA2'] = 'internal-to-mg'

    return current_db, invert_db


def add_to_database(name, link, current_db, invert_db, fsock):

    fsock.write("%s %s\n" % (name, link))
    current_db[name] = link
    invert_db[link] = name

def FR_update(current_db, invert_db):

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


    base_db = open("model_database.dat","a")
    text = text.decode()
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
            ans = input("D you want to update the database (y/n)")
            if ans == "y":
                add_to_database(modelname, link, current_db, invert_db, base_db)
        else:
            print(("        NEW model: %s" % modelname))
            ans = input("Do you want to add it to the database (y/n)")
            if ans == "y":
                add_to_database(modelname, link, current_db, invert_db, base_db)
    base_db.close()
    f = open("last_fr_check", "w")
    f.write(repr(today))
    f.close()


def CMS_update(current_db, invert_db):
    
    
    last_check = eval(open("last_cms_check").read())
    #print('CMS:', last_check)

    this_year = today.year
    months = {1:'Jan', 2:'Feb', 3: "Mar", 4:"Apr", 5:"May",6:"Jun", 7:"Jul", 8: "Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
    this_month = today.month
    this_day = today.day
    print((this_year, this_month, this_day))

    import ssl

    # This restores the same behavior as before.
    context = ssl._create_unverified_context()

    print("https://cms-project-generators.web.cern.ch/cms-project-generators/")
    data = urllib.request.urlopen("https://cms-project-generators.web.cern.ch/cms-project-generators/", context=context)

    #<img src="/_shared_static_content/icons/compressed.gif" alt="[   ]"> <a href="2HDM4MG5-may15.tar.gz">2HDM4MG5-may15.tar.gz</a>                                             2024-05-07 14:19   57K 
    import re
#pattern = '''\<dt class="attachment"\>'''
    pattern = re.compile(r'<img src="/_shared_static_content/icons/compressed.gif" alt="\[   \]"> <a href="([\w\d\.-]+)">.*</a>\s+(\d\d\d\d)-(\d\d)-(\d\d)')

    text = data.read()

    base_db = open("model_database.dat","a")
    text = text.decode()
    for match in pattern.finditer(text):
        link, year, month, day = match.groups()
        generated = datetime.date(int(year), int(month), int(day))
        print(generated, last_check, generated-last_check)
        if ((generated - last_check).days <  0): 
            continue
        if not link.endswith(('.tar.gz','.gz','.zip','.tgz','.tar')):
            continue
        author = "CMS"
        print(("found new attachment: %s by %s" % (link, author)))
        link= "https://cms-project-generators.web.cern.ch/cms-project-generators/"+link
        
        if link in invert_db:
            print(("        update of old link for model %s " % invert_db[link]))
            continue
        modelname = check_database.validate_UFO_link(link)
        if not modelname:
            print("        Not valid UFO model")
        elif modelname in current_db:
            if 'feynrules' in current_db[modelname]:
                print('already model with this name from FR')
                continue
            elif 'madgraph.' in current_db[modelname]:
                continue
            elif 'internal' in current_db[modelname]:
                continue
            elif current_db[modelname].startswith('./'):
                continue
            print(("        found modelname %s duplicate with existing model: %s" % (modelname,current_db[modelname])))
            ans = input("Do you want to update the database (y/n)")
            if ans == "y":
                add_to_database(modelname, link, current_db, invert_db, base_db)
        else:
            print(("        NEW model: %s" % modelname))
            ans = "y" #input("Do you want to add it to the database (y/n)")
            if ans == "y":
                add_to_database(modelname, link, current_db, invert_db, base_db)

    f = open("last_cms_check", "w")
    f.write(repr(today))
    f.close()

if "__main__" == __name__:
    current_db, invert_db = get_modeldatabase()
    FR_update(current_db, invert_db)
    #current_db, invert_db = get_modeldatabase()
    CMS_update(current_db, invert_db)
