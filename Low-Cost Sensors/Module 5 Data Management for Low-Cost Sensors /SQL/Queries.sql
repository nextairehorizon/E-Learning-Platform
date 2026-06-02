/* Q01: Sensors and Their Locations */
SELECT S.SensorID, S.Type, T.Location
FROM Sensor AS S
INNER JOIN Station AS T
ON S.StationID = T.StationID;


/* Q02: Sensors Located in Austria */
SELECT S.SensorID, S.Type, S.StationID, T.Location
FROM Sensor AS S
INNER JOIN Station AS T
ON S.StationID = T.StationID
WHERE T.Location LIKE '%, Austria';


/* Q03: Number of Sensors per Station */
SELECT T.StationID,
       T.Location,
       COUNT(S.SensorID) AS NumberOfSensors
FROM Station AS T
LEFT OUTER JOIN Sensor AS S
ON T.StationID = S.StationID
GROUP BY T.StationID, T.Location
ORDER BY T.StationID ASC;


/* Q04: Stations with More Than One Sensor */
SELECT T.StationID,
       T.Location,
       COUNT(S.SensorID) AS NumberOfSensors
FROM Station AS T
INNER JOIN Sensor AS S
ON T.StationID = S.StationID
GROUP BY T.StationID, T.Location
HAVING COUNT(S.SensorID) > 1
ORDER BY NumberOfSensors DESC;


/* Q05: Sensors Used in Campaigns */
SELECT C.CampaignID,
       C.Name AS CampaignName,
       S.SensorID,
       S.Type,
       S.Channel_1,
       S.Channel_2
FROM Campaign AS C
INNER JOIN SensorCampaign AS SC
ON C.CampaignID = SC.CampaignID
INNER JOIN Sensor AS S
ON SC.SensorID = S.SensorID
ORDER BY C.CampaignID ASC,
         S.SensorID ASC;
