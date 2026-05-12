import requests
import json

def test_registration():
    url = "http://localhost:8001/auth/register"
    data = {
        "email": "test_user@example.com",
        "password": "Password123!"
    }
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration()
