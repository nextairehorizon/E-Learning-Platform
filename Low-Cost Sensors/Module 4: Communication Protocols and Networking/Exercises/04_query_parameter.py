"""
Simple Server that takes query parameters
"""

# Use FastAPI as the HTTP server implementation
from fastapi import FastAPI

# Instantiate the server
app = FastAPI()

# Give the request two query parameters, both are required
@app.get("/required")
async def required(name: str, value: float):
    return f"Hello to the both required query parameters {name} with {value}."

# Give the request two query parameters, only the name is required
@app.get("/optional")
async def optional(name: str, value: float | None = None):
    return f"Hello from the server to the required {name} and the optional {value}."

# Give the request two query parameters, value has a default
@app.get("/default")
async def default(name: str, value: float = 12.34):
    return f"Hello from the server to the required {name} and the default value {value}."

