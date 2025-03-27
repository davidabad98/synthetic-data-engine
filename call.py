import requests

# Define the URL
url = "https://h2go7v00tc.execute-api.us-east-1.amazonaws.com/prod/synthetic-data"

# Set up the query parameter
params = {"model_used": "groq"}

# Send the GET request
response = requests.get(url, params=params)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("Response:", response.text)
else:
    print(f"Request failed -  {response.text}")