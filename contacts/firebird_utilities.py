"""A Firebird (tested on 1.5) version of utilities
"""
import kinterbasdb

updatestmt = '''update persons set fname = ?, lname = ?, profession = ?,
                    salutation = ?
                    where id = ?'''

insertstmt = '''insert into persons(fname, lname, profession, salutation)
                     values (?, ?, ?, ?)'''

def dbi():
    dbi = kinterbasdb.connect(database='C:\Dev\RealWorldSample\persdb.fdb',
                              host='localhost',
                              user='SYSDBA', password='masterkey')
    return dbi


def duplic(fname,lname,msg,ok):
    dup = False
    db = dbi()
    curs = db.cursor()
    curs.execute('''select * from persons where fname = '%s'
                and lname='%s' ''' % (fname,lname))
    row = curs.fetchone()
    if row:
        ok = False
        msg += "Duplicate Entry: %s" %(item)
    return msg, ok


def duplicedit(fname,lname,id,msg,ok):
    dup = False
    db = dbi()
    curs = db.cursor()
    curs.execute('''select * from persons where fname = '%s'
                and lname='%s' and id != %s''' % (fname,lname,id))
    row = curs.fetchone()
    if row:
        ok = False
        #msg += "Duplicate Entry: %s" %(item)
        msg += "Duplicate Entry: %s %s" %(fname, lname)
    return msg, ok
 
def getpersonparms(id):
    db = dbi()
    cur = db.cursor()
    cur.execute("select * from persons where id = %s" %(id))
    k = cur.fetchonemap() 
    return k
 
def getpersons():
    db = dbi() 
    cur = db.cursor()
    cur.execute("select * from persons order by lname,fname") 
    li = cur.fetchallmap()
    return li 

def getname(id): 
    res = ''
    db = dbi() 
    try:
        cur = db.cursor() 
        cur.execute('''select fname from persons
                 where id = %s''' %(id)) 
        res = cur.fetchone()[0]
    except: 
        pass
    return res 

def getid(fname,lname): 
    res = ''
    db = dbi() 
    cur = db.cursor()
    try: 
        cur.execute('''select id from persons
                     where fname = '%s' and lname='%s' ''' %(fname,lname)) 
        res = cur.fetchone()[0]
    except: 
        pass
    return res 

def deleteperson(id): 
    con = dbi()
    c = con.cursor() 
    delete = 0
    try: 
        c.execute('''delete from persons
                  where id = %s''' % (int(id))) 
        con.commit()
    except: 
        delete = 1
    return delete 

def updateperson(parms,id): 
    con = dbi()
    c = con.cursor()
    # coding style 1
    if True == 0:
        c.execute('''update persons
                     set lname='%s', fname='%s', salutation='%s',
                     profession='%s'
                     where id = %s''' 
                     % (parms['lname'],parms['fname'],parms['salutation'],
                        parms['profession'],id)) 

    # coding style 2
    elif True == 0:
        c.execute(updatestmt, (parms['fname'],
                               parms['lname'],
                               parms['profession'],
                               parms['salutation'],
                               id))

    # coding style 3
    elif True == 1:
        parms['id'] = id

        c.execute('''update persons  
                   set lname='%(lname)s', fname='%(fname)s',
                   salutation='%(salutation)s',
                   profession='%(profession)s'
                   where id = %(id)s''' % parms)

    con.commit() 

def enterperson(parms): 
    con = dbi()
    c = con.cursor()
    # coding style 1
    if True == 0:
        c.execute('''insert into persons(fname, lname, profession, salutation)
                         values ('%(fname)s', '%(lname)s', '%(profession)s',
                         '%(salutation)s')'''
                         % parms)

    # coding style 2
    elif True == 0:
        c.execute(insertstmt, (parms['fname'],
                               parms['lname'],
                               parms['profession'],
                               parms['salutation']))

    # coding style 3
    elif True == 1:
        c.execute('''insert into persons (fname, lname, profession, salutation)
                        values ('%(lname)s', '%(fname)s', '%(profession)s',
                        '%(salutation)s')''' % parms)
        
    con.commit()
