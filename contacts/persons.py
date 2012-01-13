from pytable.schemabuilder import *

schema = database(
         name="addressdemo",
         comment = """Database for the "ready-to-run" wxPython demo""",
         tables = [
                 table(
                         "persons",
                         comment ="""Storage for the simple person-editing demo""",
                         fields = [
                                 field(
                                         # PostgreSQL's serial type is not supported by many database engines
                                         "id", "integer", 0, """Serial identity field for the person""",
                                         constraints=[ unique()],
                                 ),
                                 field(
                                         "fname", "varchar", 25, """Given (first) name for the individual""",
                                         defaultValue = "''",
                                         constraints=[ notNull()],
                                 ),
                                 field(
                                         "lname", "varchar", 25, """Family (last) name for the individual""",
                                         defaultValue = "''",
                                         constraints=[ notNull()],
                                 ),
                                 field(
                                         "salutation", "varchar", 10, """Appropriate greeting/salutation for written correspondence""",
                                         defaultValue = "''",
                                         constraints=[ notNull()],
                                 ),
                                 field(
                                         "profession", "varchar", 25, """Profession in which the individual is involved""",
                                         defaultValue = "''",
                                         constraints=[ notNull()],
                                 ),
                         ],
                         indices = [
                                 index( name='personkey', primary=True, fields=('fname','lname') ),
                         ],
                 ),
         ],
)
