
DROP SCHEMA gtfs_raw CASCADE;
 CREATE SCHEMA gtfs_raw;

CREATE TABLE gtfs_raw.calendar_dates (
service_id smallint not null,
date_ bigint not null ,
exception_type smallint not null
);
CREATE TABLE gtfs_raw.calendar(
service_id smallint not null,
 monday smallint not null,
 tuesday smallint not null,
 wednesday smallint not null,
 thursday smallint not null,
 friday smallint not null,
 saturday smallint not null,
 sunday smallint not null,
 start_date bigint not null,
 end_date bigint not null
);

CREATE TABLE gtfs_raw.routes(
route_id int PRIMARY KEY,
agency_id smallint NOT NULL,
route_short_name TEXT NOT NULL,
route_long_name TEXT NOT NULL,
route_desc TEXT,
route_type smallint NOT NULL,
route_url TEXT,
route_color  CHAR(6) NOT NULL,
route_text_color CHAR(6)

);

CREATE TABLE gtfs_raw.stop_times(
trip_id bigint NOT NULL,
arrival_time interval NOT NULL,
departure_time interval NOT NULL,
stop_id int NOT NULL,
stop_sequence smallint NOT NULL,
stop_headsign TEXT ,
pickup_type smallint NOT NULL,
drop_off_type smallint NOT NULL,
shape_dist_traveled numeric(7,4) DEFAULT 0 
);

CREATE TABLE gtfs_raw.stops(
stop_id INT PRIMARY KEY,
stop_code TEXT NOT NULL,
stop_name TEXT NOT NULL,
stop_desc TEXT ,
stop_lat TEXT NOT NULL,
stop_lon TEXT NOT NULL,
zone_id SMALLINT,
stop_url TEXT,
location_type TEXT ,
parent_station INT ,
wheelchair_boarding SMALLINT 
);

CREATE TABLE gtfs_raw.trips(
route_id INT NOT NULL,
service_id SMALLINT NOT NULL,
trip_id BIGINT NOT NULL,
trip_headsign TEXT NOT NULL,
trip_short_name TEXT,
direction_id SMALLINT NOT NULL,
block_id BIGINT NOT NULL,
shape_id INT NOT NULL,
wheelchair_accessible SMALLINT NOT NULL
);

DROP SCHEMA IF EXISTS gtfs CASCADE;
CREATE SCHEMA gtfs;
GRANT USAGE ON SCHEMA gtfs to public;

CREATE TABLE gtfs.calendar_dates (
service_id smallint not null,
date_ DATE not null ,
exception_type smallint not null
);
CREATE TABLE gtfs.calendar(
service_id smallint not null,
 monday boolean not null,
 tuesday boolean not null,
 wednesday boolean not null,
 thursday boolean not null,
 friday boolean not null,
 saturday boolean not null,
 sunday boolean not null,
 start_date DATE not null,
 end_date dATE not null
);

CREATE TABLE gtfs.routes(
route_id int PRIMARY KEY,
agency_id smallint NOT NULL,
route_short_name TEXT NOT NULL,
route_long_name TEXT NOT NULL,
route_desc TEXT,
route_type smallint NOT NULL,
route_url TEXT,
route_color  CHAR(6) NOT NULL,
route_text_color CHAR(6)

);

CREATE TABLE gtfs.stop_times(
trip_id bigint PRIMARY KEY,
arrival_time interval NOT NULL,
departure_time interval NOT NULL,
stop_id int NOT NULL,
stop_sequence smallint NOT NULL,
stop_headsign TEXT ,
pickup_type smallint NOT NULL,
drop_off_type smallint NOT NULL,
shape_dist_traveled numeric(7,4) DEFAULT 0 
);

CREATE TABLE gtfs.stops(
stop_id INT PRIMARY KEY,
stop_code TEXT NOT NULL,
stop_name TEXT NOT NULL,
stop_desc TEXT ,
stop_lat TEXT NOT NULL,
stop_lon TEXT NOT NULL,
zone_id SMALLINT,
stop_url TEXT,
location_type TEXT ,
parent_station INT ,
wheelchair_boarding SMALLINT 
);

CREATE TABLE gtfs.trips(
route_id INT NOT NULL,
service_id SMALLINT NOT NULL,
trip_id BIGINT NOT NULL,
trip_headsign TEXT NOT NULL,
trip_short_name TEXT,
direction_id SMALLINT NOT NULL,
block_id BIGINT NOT NULL,
shape_id INT NOT NULL,
wheelchair_accessible SMALLINT NOT NULL
);