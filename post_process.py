import json

data = json.load(open("result.json"))

institutions = {}

for item in data:
    if item["type"] == "institution":
        code = item["code"]
        item["provider_id"] = int(item["provider_id"])
        del item["code"]
        item["courses"] = {}
        item["contacts"] = []
        institutions[code] = item
    if item["type"] == "contact":
        institution = institutions[item["institution"]]
        institution["contacts"].append(item)
    if item["type"] == "course":
        institution_code = item["institution"]
        code = item["code"]
        institution = institutions[institution_code]
        institution["courses"][code] = {
            "name": item["name"]
        }

json.dump(institutions, open("institutions.json", "w"))
