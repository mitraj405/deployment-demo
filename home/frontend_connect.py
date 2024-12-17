import requests

def send_db_connection_request(hostname, username, password, dbname):
    # Flask backend URL where the database connection requests are handled
    FLASK_BACKEND_URL = 'http://localhost:5000/connect'  # Adjust the URL based on your actual Flask app URL

    # Prepare the payload to send as JSON
    payload = {
        'hostname': hostname,
        'username': username,
        'password': password,
        'dbname': dbname,
        'port': port
    }
    
    # Send the POST request to the Flask backend
    response = requests.post(FLASK_BACKEND_URL, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Response from backend:", response.json())
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    # Example of sending database connection details
    hostname="mysql-3562afe5-bawsny-169c.e.aivencloud.com"
    username="avnadmin"
    password="AVNS_BsudL5xLd8oWrMb8Bzf"
    dbname="defaultdb"
    port = "20609"
    send_db_connection_request(hostname, username, password, dbname)
