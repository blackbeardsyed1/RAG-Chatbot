import requests

# Define the API endpoint
url = "http://127.0.0.1:8080/process-queries/"

# The raw query string to send to the API
raw_query = 'Which subject has highest quiz average score and highest assignment score in Spring 2021, Give the Subject Titles rather than course code. What are top 3 InterBoard based on Fsc scores.'

# Define the payload to send in the POST request
payload = {
    "query": raw_query
}

# Send the POST request
response = requests.post(url, json=payload)

# Print the response from the API
if response.status_code == 200:
    print("Final Output:", response.json().get("final_output"))
else:
    print("Error:", response.json().get("detail"))
