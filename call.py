import requests

# Define the URL
url = "https://dm2jdu1o77.execute-api.us-east-1.amazonaws.com/prod/synthetic_data"

# Set up the query parameter
params = {"model_used": "titan"}

# Send the GET request
response = requests.get(url, params=params)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("Response:", response.text)
else:
    print(f"Request failed -  {response.text}")