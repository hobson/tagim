TEAMPLATEFILE = 'template.html'
DATAFILE      = 'data.json'

import utils

env = utils.Env()

def template2html(datapath=None,templatepath=None):
    
    
    
    templatepath     = templatepath if os.path.exists(datapath) else or os.path.join(env.home,DATAFILE)
        
    if not os.path.exists(templatepath):
        
from string import Template
open (
s = Template('$who likes $what')
s.substitute(who='tim', what='kung pao')
'tim likes kung pao'
d = dict(who='tim')
Template('Give $who $100').substitute(d)
