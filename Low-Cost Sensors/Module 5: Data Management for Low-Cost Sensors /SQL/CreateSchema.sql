DROP TABLE IF EXISTS SensorCampaign;
DROP TABLE IF EXISTS Campaign;
DROP TABLE IF EXISTS Sensor;
DROP TABLE IF EXISTS Station;

CREATE TABLE Station (
    StationID CHAR(5) PRIMARY KEY,
    Location VARCHAR(128) NOT NULL
);

CREATE TABLE Sensor (
    SensorID INTEGER PRIMARY KEY,
    Type VARCHAR(128) NOT NULL,
    Channel_1 VARCHAR(128),
    Channel_2 VARCHAR(128),
    StartDate DATE,
    StationID CHAR(5) NOT NULL,
    FOREIGN KEY (StationID)
        REFERENCES Station(StationID)
);

CREATE TABLE Campaign (
    CampaignID INTEGER PRIMARY KEY,
    Name VARCHAR(128) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,
    ValidatedBy INTEGER,
    FOREIGN KEY (ValidatedBy)
        REFERENCES Sensor(SensorID)
);

CREATE TABLE SensorCampaign (
    SensorID INTEGER,
    CampaignID INTEGER,
    PRIMARY KEY (SensorID, CampaignID),
    FOREIGN KEY (SensorID)
        REFERENCES Sensor(SensorID),
    FOREIGN KEY (CampaignID)
        REFERENCES Campaign(CampaignID)
);
