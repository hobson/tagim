#!/usr/bin/env python
"""Compose an e-mail URL and launch firefox to edit it further

example usage:
./email.py -s 'Hello World' -b "I didn't know you could accept e-mails!" -e hello@world.com -c info@world.com
"""

import urllib
import os, sys
from optparse import OptionParser
import datetime

p = OptionParser()
p.add_option("-e", "-t", "--email",dest='email', default='journal@totalgood.com',
             help="Send email to EMAIL_TO", metavar="EMAIL_TO")
p.add_option("-q", "--quiet",
             action="store_false", dest="verbose", default=True,
             help="Don't print status messages to stdout")
p.add_option("-s", "--subject", "--subj",
             default='Journal '+datetime.datetime.today().isoformat(' '),
             help="Subject line of email message")
p.add_option("-c", "--cc",help="Carbon copy email addresses")
p.add_option("-f", "--firefox", 
             action="store_true", default=False,
             help="Use firefox (its email helper application) to compose the e-mail")
p.add_option("-b", "--body",help="Email body text")
p.add_option("--evolution", 
             action="store_true", dest="firefox", default=False,
             help="Use evolution rather than firefox to compose the e-mail")


(o, a) = p.parse_args()

print('Email options being used by '+sys.argv[0]+':')
print(str(o))
print(o)
print(type(o))
od=dict(vars(o))

email=od.pop('email')
firefox=od.pop('firefox')
verbose=od.pop('verbose')

# but this won't leave any blank values in the options dictionary?!
for k,v in od.items(): 
  if not v:
    od.pop(k)

print('Fields being sent to email program in "emailto:" URL:')
print(od)

#f = urllib.urlopen()
apps = ['/usr/bin/evolution','/usr/bin/firefox']
clargs = '"mailto:'+email+'?'+od.items()[0][0]+'='+urllib.quote(od.items()[0][1])
for odi in od.items()[1:]:
  clargs += '&'+odi[0]+'='+urllib.quote(odi[1])
clargs += '"'
print 'cl: '+apps[int(firefox)]+' '+clargs
# for some reason the execl and execlp versions just don't seem to pass along the command line arguments like I'd expect them too
# actHL: create a shell script of python script that displays the command line string and see what's actually being sent when these exec* versions are used
#os.execl(apps[int(firefox)],clargs)
#os.execlp(apps[int(firefox)],clargs)
os.system(apps[int(firefox)]+' '+clargs)

