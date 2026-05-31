"""
Simple Server with one get method that counts the queries
"""

# Use FastAPI as the HTTP server implementation
from fastapi import FastAPI

# Instantiate the server
app = FastAPI()

# stored the counter
counter = 0

# Give the server one endpoint
@app.get("/hello")
async def hello_counter():
    # Do not initiate the variable locally, but use the global one we already have
    global counter
    counter += 1
    return f"Hello from the server for the {counter} time."

