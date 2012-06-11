create table persons(
        id serial unique,
        fname varchar(25) not null,
        lname varchar(25) not null,
        salutation varchar(10) not null,
        profession varchar(25) not null,
        CONSTRAINT personkey primary key(fname,lname)
        );
