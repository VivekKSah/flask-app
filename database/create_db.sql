CREATE USER test_user WITH PASSWORD 'test123';
ALTER USER test_user WITH SUPERUSER;


CREATE DATABASE test_database
  WITH TEMPLATE = template0
       OWNER = test_user
        ENCODING = 'UTF8';


\c test_database 


CREATE SCHEMA "microcam"
  AUTHORIZATION test_user;


CREATE TABLE microcam.user_details
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address VARCHAR(200) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

--ALTER TABLE microcam.user_details
--ADD COLUMN user_id INTEGER;

ALTER TABLE microcam.user_details
  OWNER TO test_user;


CREATE TABLE microcam.images
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    filename VARCHAR(200) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES microcam.user_details (id)
);

ALTER TABLE microcam.images
  OWNER TO test_user;


CREATE TABLE microcam.image_shares
(
    id SERIAL PRIMARY KEY,
    image_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (image_id) REFERENCES microcam.images (id),
    FOREIGN KEY (user_id) REFERENCES microcam.user_details (id)
);

ALTER TABLE microcam.image_shares
  OWNER TO test_user;


CREATE TABLE microcam.contact_us
(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE microcam.contact_us
  OWNER TO test_user;
