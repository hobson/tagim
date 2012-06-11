CREATE GENERATOR GEN_PERSONS_ID;
create table persons( 
        id integer not null, 
        fname varchar(25) not null, 
        lname varchar(25) not null, 
        salutation varchar(10) not null, 
        profession varchar(25) not null, 
        CONSTRAINT personkey primary key(fname,lname) 
        );
CREATE TRIGGER PERSONS_BI0 FOR PERSONS
ACTIVE BEFORE INSERT POSITION 0
AS BEGIN
      IF(NEW."ID" IS NULL) THEN NEW."ID" = GEN_ID("GEN_PERSONS_ID",1);
    END;
