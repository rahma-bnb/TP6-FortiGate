import os
import requests

FORTIGATE_IP = "192.168.116.128"

TOKEN = os.environ["FORTIGATE_TOKEN"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

url = f"https://{FORTIGATE_IP}/api/v2/cmdb/firewall/address"

resp = requests.get(
    url,
    headers=headers,
    verify=False,
    timeout=20
)

print("FortiGate API status:", resp.status_code)

if resp.status_code == 200:
    print("Deploy simulation OK")
else:
    raise Exception("FortiGate connection failed")
