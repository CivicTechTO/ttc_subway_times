# instructions:

log into postgres and run:

`createdb service_alerts;`

Next create a new user by running:

`createuser pi --pwprompt`

Switch into the database:

`\connect service_alerts`

Create a new table with:

`CREATE TABLE service_alerts_tb (
  id BIGSERIAL PRIMARY KEY,
  a_type varchar,
  a_time integer,
  a_text varchar);`

Lastly, we have to grant PRIVILEGES to the new user
`GRANT ALL PRIVILEGES ON TABLE service_alerts_tb TO pi;
 GRANT USAGE, SELECT ON SEQUENCE service_alerts_tb_id_seq TO pi;`
