"""
Simple Server that takes data via POST, delivers the data via GET, 
updates data via PUT, and deletes data via DELETE
"""

# Use FastAPI as the HTTP server implementation
from fastapi import FastAPI
# Use Pydantic to enforce a data model
from pydantic import BaseModel

# Instantiate the server
app = FastAPI()


# Define our data model
class Measurement(BaseModel):
    name: str
    value: float

# Store the data we get
measurements = {}


# Add a new measurement
@app.post("/measurements")
async def create(measurement: Measurement):
    measurement_id = len(measurements) + 1
    measurements[measurement_id] = measurement
    return {"id": measurement_id, "measurement": measurement}

# Get a specific measurement
@app.get("/measurements")
async def read(id: int):
    return measurements.get(id, {"error": "ID not found"})

# Update a specific measurement
@app.put("/measurements")
async def update(id: int, measurement: Measurement):
    if id in measurements:
        measurements[id] = measurement
        return {"message": "Measurement updated", "measurement": measurement}
    return {"error": "Measurement not found"}

# Delete a specific measurement
@app.delete("/measurements")
async def delete(id: int):
    if id in measurements:
        deleted_measurement = measurements.pop(id)
        return {"message": "Measurement deleted", "measurement": deleted_measurement}
    return {"error": "Measurement not found"}
