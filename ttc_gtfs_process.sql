INSERT INTO gtfs.calendar

SELECT service_id, monday = 1,
 tuesday = 1,
 wednesday = 1,
 thursday = 1,
 friday = 1,
 saturday = 1,
 sunday = 1,
 to_date(start_date::TEXT, 'YYYYMMDD'),
 to_date(end_date::TEXT, 'YYYYMMDD')
  FROM gtfs_raw.calendar;

INSERT INTO gtfs.calendar_dates
SELECT service_id, to_date(date_::TEXT, 'YYYYMMDD'), exception_type
  FROM gtfs_raw.calendar_dates;


INSERT INTO gtfs.routes SELECT * FROM gtfs_raw.routes;
INSERT INTO gtfs.stop_times SELECT * FROM gtfs_raw.stop_times;
INSERT INTO gtfs.stops SELECT * FROM gtfs_raw.stops;
INSERT INTO gtfs.trips SELECT * FROM gtfs_raw.trips;
