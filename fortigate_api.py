
import os
import requests
import urllib3
from dotenv import load_dotenv

# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

FORTIGATE_HOST = os.getenv("FORTIGATE_HOST", "").rstrip("/")
FORTIGATE_TOKEN = os.getenv("FORTIGATE_TOKEN")

if not FORTIGATE_HOST or not FORTIGATE_TOKEN:
    raise ValueError("Missing FortiGate configuration in .env file")

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

BASE_URL = f"{FORTIGATE_HOST}/api/v2/cmdb"

HEADERS = {
    "Authorization": f"Bearer {FORTIGATE_TOKEN}",
    "Content-Type": "application/json"
}


# ==========================================
# 2. GET FIREWALL ADDRESSES
# ==========================================

def get_addresses():

    url = f"{BASE_URL}/firewall/address"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            verify=False,
            timeout=15
        )

        response.raise_for_status()

        addresses = response.json().get("results", [])

        print("\n========== FIREWALL ADDRESSES ==========")

        for address in addresses:
            print(
                "Name:", address.get("name"),
                "| Subnet:", address.get("subnet"),
                "| Type:", address.get("type")
            )

        print("\nTotal objects:", len(addresses))

        return addresses

    except requests.exceptions.RequestException as error:
        print("Address Error:", error)
        return []


# ==========================================
# 3. CREATE ADDRESS OBJECT
# ==========================================

def create_address(name, subnet):

    url = f"{BASE_URL}/firewall/address"

    try:
        check = requests.get(
            url,
            headers=HEADERS,
            params={"filter": f"name=={name}"},
            verify=False,
            timeout=15
        )

        check.raise_for_status()

        existing = check.json().get("results", [])

        for obj in existing:
            if obj.get("name") == name:
                print(f"\nAddress '{name}' already exists.")
                return

        payload = {
            "name": name,
            "type": "ipmask",
            "subnet": subnet
        }

        response = requests.post(
            url,
            json=payload,
            headers=HEADERS,
            verify=False,
            timeout=15
        )

        response.raise_for_status()

        print(f"\nSUCCESS: Address '{name}' created!")
        print(response.json())

    except requests.exceptions.RequestException as error:
        print("\nAddress Creation Error:", error)

        if "response" in locals():
            print("Response:", response.text)


# ==========================================
# 4. CREATE VIRTUAL IP (VIP)
# ==========================================

def create_vip():

    url = f"{BASE_URL}/firewall/vip"

    vip_name = "VIP-HTTPS-WEB-01"

    try:
        check = requests.get(
            url,
            headers=HEADERS,
            params={"filter": f"name=={vip_name}"},
            verify=False,
            timeout=15
        )

        check.raise_for_status()

        existing = check.json().get("results", [])

        for vip in existing:
            if vip.get("name") == vip_name:
                print(f"\nVIP '{vip_name}' already exists.")
                return

        payload = {
            "name": vip_name,
            "extip": "192.168.192.10",
            "mappedip": [
                {"range": "10.0.10.50"}
            ],
            "extintf": "port2",
            "portforward": "enable",
            "protocol": "tcp",
            "extport": "443",
            "mappedport": "443"
        }

        response = requests.post(
            url,
            json=payload,
            headers=HEADERS,
            verify=False,
            timeout=15
        )

        response.raise_for_status()

        print(f"\nSUCCESS: VIP '{vip_name}' created!")
        print(response.json())

    except requests.exceptions.RequestException as error:
        print("\nVIP Creation Error:", error)

        if "response" in locals():
            print("Response:", response.text)


# ==========================================
# 5. CREATE FIREWALL POLICY
# ==========================================

def create_firewall_policy():

    url = f"{BASE_URL}/firewall/policy"

    policy_name = "ALLOW-HTTPS-TO-WEB"

    try:
        check = requests.get(
            url,
            headers=HEADERS,
            verify=False,
            timeout=15
        )

        check.raise_for_status()

        policies = check.json().get("results", [])

        for policy in policies:
            if policy.get("name") == policy_name:
                print(f"\nPolicy '{policy_name}' already exists.")
                return

        # Find an unused policy ID
        used_ids = [
            int(policy["policyid"])
            for policy in policies
            if policy.get("policyid") is not None
        ]

        new_id = max(used_ids, default=0) + 1

        payload = {
            "policyid": new_id,
            "name": policy_name,
            "srcintf": [
                {"name": "port2"}
            ],
            "dstintf": [
                {"name": "port3"}
            ],
            "srcaddr": [
                {"name": "all"}
            ],
            "dstaddr": [
                {"name": "VIP-HTTPS-WEB-01"}
            ],
            "action": "accept",
            "schedule": "always",
            "service": [
                {"name": "HTTPS"}
            ],
            "nat": "disable",
            "status": "enable"
        }

        response = requests.post(
            url,
            json=payload,
            headers=HEADERS,
            verify=False,
            timeout=15
        )

        response.raise_for_status()

        print(
            f"\nSUCCESS: Policy '{policy_name}' created!"
        )

        print(response.json())

    except requests.exceptions.RequestException as error:
        print("\nPolicy Creation Error:", error)

        if "response" in locals():
            print("Response:", response.text)


# ==========================================
# 5.1 GET FIREWALL POLICIES
# ==========================================

def get_firewall_policies():

    url = f"{BASE_URL}/firewall/policy"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            verify=False,
            timeout=15
        )

        response.raise_for_status()

        policies = response.json().get("results", [])

        print("\n========== FIREWALL POLICIES ==========")

        for policy in policies:
            print(
                "ID:", policy.get("policyid"),
                "| Name:", policy.get("name"),
                "| Action:", policy.get("action"),
                "| Status:", policy.get("status")
            )

        print("\nTotal policies:", len(policies))

    except requests.exceptions.RequestException as error:
        print("Policy Error:", error)
# ==========================================
# 6. MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    print("\n================================")
    print(" FORTIGATE AUTOMATION PROJECT")
    print("================================")

    # Display existing addresses
    get_addresses()

    # Create address if absent
    create_address(
        "SRV-WEB-01",
        "10.0.10.50/32"
    )

    # Create VIP if absent
    create_vip()

    # Create firewall policy if absent
    create_firewall_policy()
    get_firewall_policies()

    print("\n================================")
    print(" AUTOMATION FINISHED")
    print("================================")
