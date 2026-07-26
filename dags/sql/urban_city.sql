CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.urban_city_requests (
	unique_key VARCHAR(100),
	created_date DATE,
	created_time TIME,
	closed_date DATE,
	closed_time TIME,
	agency_name TEXT,
	problem TEXT,
	problem_detail TEXT,
	additional_details TEXT,
	location_type VARCHAR(250),
	incident_zip VARCHAR(100),
	incident_address TEXT,
	street_name TEXT,
	city VARCHAR(100),
	status TEXT,
	borough VARCHAR(100),
	latitude DOUBLE PRECISION,
	longitude  DOUBLE PRECISION	
);