COPY Station
FROM 'C:\Users\YourName\sensor_data\Station.csv'
CSV HEADER DELIMITER ',';

COPY Sensor
FROM 'C:\Users\YourName\sensor_data\Sensor.csv'
CSV HEADER DELIMITER ',';

COPY Campaign
FROM 'C:\Users\YourName\sensor_data\Campaign.csv'
CSV HEADER DELIMITER ',';

COPY SensorCampaign
FROM 'C:\Users\YourName\sensor_data\SensorCampaign.csv'
CSV HEADER DELIMITER ',';
