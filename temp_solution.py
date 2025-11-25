import requests
import json

# Define the JSON data
data = {
  "email": "student@example.com",
  "secret": "TEST_SECRET",
  "url": "https://tds-llm-analysis.s-anand.net/demo",
  "answer": "anything you want"
}

# Convert the data to JSON format
json_data = json.dumps(data)

# Set the headers for the POST request
headers = {
    'Content-Type': 'application/json'
}

# Send the POST request
response = requests.post('https://tds-llm-analysis.s-anand.net/submit', headers=headers, data=json_data)

# Check if the request was successful
if response.status_code == 200:
    print("The JSON data was successfully posted.")
else:
    print("Failed to post the JSON data. Status code: ", response.status_code)

# Print the answer
print("The answer is: anything you want")