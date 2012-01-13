import psycopg


def dbi():
    dbi = psycopg.connect("dbname=persdb host=localhost\
    user=postgres password=postgres")
    return dbi


def duplic(fname,lname,msg,ok):
    dup = False
    db = dbi()
    curs = db.cursor()
    curs.execute("select * from persons where fname = '%s'\
                and lname='%s'" % (fname,lname))
    row = curs.fetchone()
    if row:
        ok = False
        msg += "Duplicate Entry: %s" %(item)
    return msg, ok


def duplicedit(fname,lname,id,msg,ok):
    dup = False
    db = dbi()
    curs = db.cursor()
    curs.execute("select * from persons where fname = '%s'\
                and lname='%s' and id != %s" % (fname,lname,id))
    row = curs.fetchone()
    if row:
        ok = False
        msg += "Duplicate Entry: %s" %(item)
    return msg, ok

def getpersonparms(id):
    db = dbi()
    cur = db.cursor()
    cur.execute("select * from persons where id = %s" %(id))
    k = cur.dictfetchone()
    return k

def getpersons():
    db = dbi()
    cur = db.cursor()
    cur.execute("select * from persons order by lname,fname")
    li = cur.dictfetchall()
    return li

def getname(id):
    res = ''
    db = dbi()
    try:
        cur = db.cursor()
        cur.execute("select fname from persons\
                 where id = %s" %(id))
        res = cur.fetchone()[0]
    except:
        pass
    return res

def getid(fname,lname):
    res = ''
    db = dbi()
    cur = db.cursor()
    try:
        cur.execute("select id from persons\
                     where fname = '%s' and lname='%s'" %(fname,lname))
        res = cur.fetchone()[0]
    except:
        pass
    return res

def deleteperson(id):
    con = dbi()
    c = con.cursor()
    delete = 0
    try:
        c.execute("delete from persons\
        where id = %s" % (int(id)))
        con.commit() 
    except:
        delete = 1
    return delete

def updateperson(parms,id):
    con = dbi()
    c = con.cursor()
    c.execute("update persons \
    set lname='%s', fname='%s', salutation='%s',profession='%s'\
     where id = %s"
    % (parms['lname'],parms['fname'],parms['salutation'],
    parms['profession'],id))
    con.commit()

def enterperson(parms):
    con = dbi()
    c = con.cursor()
    c.execute("insert into persons(fname,lname,profession,salutation)\
       values ('%s', '%s', '%s', '%s')" % (parms['fname'],
       parms['lname'],parms['profession'],parms['salutation']))
    con.commit()
