from pytable import dbspecifier, sqlquery
import traceback

# this would normally be parameterised and stored somewhere...
SPECIFIER = dbspecifier.DBSpecifier(
         database = "addressdemo",
         drivername = "PyPgSQL",
)
##SPECIFIER = dbspecifier.DBSpecifier(
##       database = ":memory:",
##       drivername = "SQLite",
##)
# Real PyTable apps use better mechanisms for accessing these...
SCHEMA = None
PERSONS = None # the only table we use
# recreating connections to in-memory databases creates new dbs,
# so for this cross-database case, we'll
CONNECTION = None

def dbi():
         """Get a configured database connection

         Side effect is to ensure that we've got a resolved db schema
         and that the schema's table exists in the database...
         """
         global SCHEMA, PERSONS, CONNECTION
         if CONNECTION is None or CONNECTION.invalid:
                 driver, CONNECTION = SPECIFIER.connect()
         connection = CONNECTION
         if SCHEMA is None:
                 import schema
                 schema.schema.resolve( driver )
                 SCHEMA = schema.schema
                 PERSONS = SCHEMA.lookupName( 'persons' )
                 if hasattr( driver, 'listTables' ):
                         tables = driver.listTables( connection )
                         if 'persons' not in tables:
                                 # need to build the database...
                                 from pytable import installschema
                                 installschema.installSchema(
                                         connection,
                                         SCHEMA,
                                 )
                                 connection.commit()
         return connection

def duplic(fname,lname,msg,ok):
         dup = False
         for record in getperson( fname,lname ):
                 return "Duplicate Entry: %s,%s %s" %(fname,lname, msg), False
         return msg, ok

def duplicedit(fname,lname,id,msg,ok):
         dup = False
         for record in getperson( fname,lname, notID = id ):
                 return "Duplicate Entry: %s,%s %s" %(fname,lname, msg), False
         return msg, ok

def getperson( fname=None, lname=None, id=None, notID=None ):
         """Get person given sub-set of parameters"""
         wheres = []
         for field,value in [
                 ('fname',fname),
                 ('lname',lname),
                 ('id',id),
         ]:
                 if value is not None:
                         wheres.append( '%(field)s=%%(%(field)s)s'%locals())
         if notID is not None:
                 wheres.append( 'id != %(notID)s' )
         if wheres:
                 wheres = ' WHERE ' + (" AND ".join( wheres ))
         else:
                 wheres = ""
         connection = dbi()
         return PERSONS.query(
                 """SELECT * FROM persons %(wheres)s ORDER BY lname,fname;""",
                 connection,
                 wheres = wheres,
                 fname = fname,
                 lname = lname,
                 id = id,
                 notID = notID,
         )

def getpersonparms(id):
         for record in getperson( id=id ):
                 return record
         raise KeyError( "Unknown person id %r"%(id,))

def getpersons():
         return getperson()

def getname(id):
         try:
                 for person in getperson(fname,lname):
                         return person.fname
         except:
                 return ''

def getid(fname,lname):
         try:
                 for person in getperson(fname,lname):
                         return person.id
         except Exception, err:
                 traceback.print_exc()
                 return ''

def deleteperson(id):
         # really should use deleteQuery on the record object...
         connection = dbi()
         delete = 0
         try:
                 PERSONS.itemClass( id = id ).deleteQuery( connection )
                 connection.commit()
         except:
                 delete = 1
                 connection.rollback()
         return delete

def updateperson(parms,id):
         connection = dbi()
         try:
                 # normally you would use a record directly to
                 # do this updating, which requires us to do an
                 # extra query to get the old primary key to do
                 # the updates...
                 person = PERSONS.itemClass( id=id )
                 person.refreshQuery( connection )
                 for key,value in parms.items():
                         setattr(person, key,value)
                 person.updateQuery( connection )
                 connection.commit()
         except Exception, err:
                 traceback.print_exc()
                 raise

def enterperson(parms):
         connection = dbi()
         try:
                 newID = 0
                 for record in sqlquery.SQLQuery(
                         """SELECT max(id) FROM persons;""",
                 )( connection ):
                         try:
                                 newID = record[0]+1
                         except TypeError, err:
                                 # attempted to add to None
                                 newID = 1
                         break
                 person = PERSONS.itemClass( id=newID, **parms )
                 person.insertQuery( connection )
                 connection.commit()
         except Exception, err:
                 traceback.print_exc()
                 raise
