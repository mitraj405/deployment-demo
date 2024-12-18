import requests
import json

# Flask backend URL (assuming it's running locally on port 5000)
FLASK_BACKEND_URL = 'http://localhost:5000/chat'

def send_message_to_backend(user_message):
    # Prepare the payload to send as JSON
    payload = {
        'message': user_message,
        'thread_from_previous_page': "thread_h1tAcL1o2VVfpWwyWbppIfmd",
        'assistant_from_previous_page':"asst_x3UrXUedieAYEQAHdas5Gwc2"
    }
    
    # Send the POST request to the Flask backend
    response = requests.post(FLASK_BACKEND_URL, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Response from backend:", response.json())
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    # Example of sending a message
    user_input = input("Enter a message for the backend: ")
    send_message_to_backend(user_input)
