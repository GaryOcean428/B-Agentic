import requests
import json

url = 'http://127.0.0.1:50001/msg'
data = {'message': 'Hello, Agent Zero!'}

print(f"Sending POST request to {url}")
print(f"Request data: {data}")

try:
    response = requests.post(url, json=data)
    print(f"Request sent successfully")

    print(f"Status Code: {response.status_code}")
    print("Response Content:")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

print("Script execution completed")
