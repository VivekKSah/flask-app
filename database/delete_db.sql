\c test_database 

DROP TABLE microcam.image_shares;
DROP TABLE microcam.images;
DROP TABLE microcam.user_details;
DROP TABLE microcam.contact_us;

DROP SCHEMA microcam;

\c postgres 

DROP DATABASE test_database;

DROP ROLE test_user;
