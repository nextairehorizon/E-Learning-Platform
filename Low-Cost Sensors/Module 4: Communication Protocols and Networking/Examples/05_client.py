"""
Simple HTTP client implemented with the requests package
"""

# library to send HTTP requests
import requests
# library to read the JSON responses
import json

# URL to our server, so that we do not need to write it each time
url = "http://localhost:8080/measurements"
# Set the content type, so that the server knows how to decode the data
headers = {"Content-Type": "application/json"}


# Sent the first measurement
print("Save the first measurement on the server")
response = requests.post(url, json={"name": "first", "value": 1.1 }, headers=headers)
print("Status code: ", response.status_code)
print("Response: ", response.text)
print("\n\n")

# ID of the measurement as returned by the server
id_1 = json.loads(response.text)["id"]

# Get the first element from the server
print("Get the first measurement from the server")
response = requests.get(url, params={"id": id_1 })
print("Status code: ", response.status_code)
print("Response: ", response.text)
print("\n\n")


# Sent two more measurements to the server
print("Save the second measurement on the server")
response = requests.post(url, json={"name": "second", "value": 2.2 }, headers=headers)
print("Status code: ", response.status_code)
print("Response: ", response.text)
print("\n")
id_2 = json.loads(response.text)["id"]

print("Save the third measurement on the server")
response = requests.post(url, json={"name": "third", "value": 3.3 }, headers=headers)
print("Status code: ", response.status_code)
print("Response: ", response.text)
id_3 = json.loads(response.text)["id"]
print("\n\n")


# Update the third measurement
print("Update the third measurement on the server")
response = requests.put(url, params={"id": id_3 }, json={"name": "new third", "value": 3333.3 }, headers=headers)
print("Status code: ", response.status_code)
print("Response: ", response.text)
print("\n")

# Get the updated third measurement from the server
print("Get the updated third measurement from the server")
response = requests.get(url, params={"id": id_3 })
print("Status code: ", response.status_code)
print("Response: ", response.text)
print("\n\n")


# Delete the second element from the server
print("Delete the second measurement from the server")
response = requests.delete(url, params={"id": id_2 })
print("Status code: ", response.status_code)
print("Response: ", response.text)
print("\n")

# Try to get the second element from the server, which will fail due to it being deleted
print("Get the second measurement from the server")
response = requests.get(url, params={"id": id_2 })
print("Status code: ", response.status_code)
print("Response: ", response.text)

