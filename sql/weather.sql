CREATE TABLE IF NOT EXISTS staging.weather (
    observation_time TIMESTAMP,
    temperature NUMERIC(5,2),
    humidity NUMERIC(5,2),
    wind_speed NUMERIC(5,2),
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT *
FROM staging.weather
ORDER BY ingestion_timestamp DESC;