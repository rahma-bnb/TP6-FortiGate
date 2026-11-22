import sys
import yaml

with open("firewall/rules.yaml") as f:
    rules = yaml.safe_load(f)["rules"]

blocked = [
    {
        "srcaddr": "LAN",
        "service": "SSH"
    }
]

errors = []

for rule in rules:
    for flow in blocked:

        if (
            rule.get("srcaddr") == flow["srcaddr"]
            and rule.get("service") == flow["service"]
            and rule.get("action") == "accept"
        ):
            errors.append(
                f"Flux interdit autorisé : {flow}"
            )

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("Tests OK")
