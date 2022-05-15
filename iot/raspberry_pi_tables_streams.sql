// STEP 1.A Create Raspberry Pi reference table

CREATE TABLE raspberry_pi_metadata (
  id STRING PRIMARY KEY
) WITH (
  kafka_topic='raspberry-pi-metadata', 
  value_format='AVRO'
);


// STEP 1.B Create readings stream

CREATE STREAM raspberry_pi_readings WITH (
  kafka_topic='raspberry-pi-readings',
  value_format='AVRO'
);


// STEP 2. Enrich stream with Raspberry Pi table data

CREATE STREAM raspberry_pi_readings_enriched WITH (
  kafka_topic='raspberry-pi-readings-enriched',
  value_format='AVRO'
) AS 
SELECT 
    raspberry_pi_readings.pi_id            AS pi_id
    raspberry_pi_readings.temperature      AS temperature,
    raspberry_pi_metadata.temperature_high AS temperature_high
FROM raspberry_pi_readings
JOIN raspberry_pi_metadata
ON raspberry_pi_readings.pi_id = raspberry_pi_metadata.pi_id
PARTITION BY raspberry_pi_readings.pi_id
EMIT CHANGES;


// STEP 3. Create high readings table with messages

CREATE TABLE raspberry_pi_high_readings WITH (   
    kafka_topic='raspberry-pi-high-readings',
    format='AVRO'
) AS SELECT
    pi_id, 
    temperature_high
    CONCAT('Raspberry Pi ', pi_id, '\'s temperature is too high at ', temperature_high) AS message,
    COUNT(*) AS high_reading_count
FROM raspberry_pi_readings_enriched
WINDOW TUMBLING (SIZE 30 MINUTES, RETENTION 7 DAYS)
WHERE temperature_high < temperature
GROUP BY pi_id, temperature_high
HAVING COUNT(*) = 180
EMIT CHANGES;
