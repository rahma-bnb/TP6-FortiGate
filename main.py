
import os
import requests
import urllib3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FORTIGATE_HOST = os.getenv("FORTIGATE_HOST")
FORTIGATE_TOKEN = os.getenv("FORTIGATE_TOKEN")

# Disable SSL warnings for our local lab
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_connection():
    if not FORTIGATE_HOST or not FORTIGATE_TOKEN:
        print("ERROR: Missing FortiGate configuration in .env")
        return

    url = f"{FORTIGATE_HOST}/api/v2/monitor/system/status"

    headers = {
        "Authorization": f"Bearer {FORTIGATE_TOKEN}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            verify=False,
            timeout=15
        )

        print("HTTP Status Code:", response.status_code)

        if response.status_code == 200:
            print("SUCCESS: Connected to FortiGate!")
            print(response.json())
        else:
            print("ERROR: API request failed")
            print(response.text)

    except requests.exceptions.RequestException as error:
        print("Connection error:", error)


if __name__ == "__main__":
    test_connection()
