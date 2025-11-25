import requests

# This simulates the Exam Server sending a task to YOUR computer
url = "http://localhost:8000/quiz"

payload = {
    "email": "student@example.com",
    "secret": "TEST_SECRET",
    # This is the demo URL provided in your prompt
    "url": "https://tds-llm-analysis.s-anand.net/demo" 
}

print("Sending request to your API...")
try:
    response = requests.post(url, json=payload)
    print("Response Code:", response.status_code)
    print("Response Body:", response.json())
except Exception as e:
    print("Error:", e)