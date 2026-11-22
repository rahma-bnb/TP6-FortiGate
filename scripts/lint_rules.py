import sys
import yaml

with open("firewall/rules.yaml") as f:
    rules = yaml.safe_load(f)["rules"]

errors = []

required = [
    "name",
    "srcintf",
    "dstintf",
    "srcaddr",
    "dstaddr",
    "service",
    "action"
]

for r in rules:

    for field in required:
        if field not in r:
            errors.append(
                f"Champ manquant {field} dans {r.get('name','unknown')}"
            )

    if r.get("srcaddr") == "all" and r.get("service") == "ALL":
        errors.append(
            f"Règle any-any interdite : {r['name']}"
        )

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("Lint OK")
