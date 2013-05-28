import json
import re
data = json.load(open("result.json"))

institutions = {}
courses = {}

for item in data:
    _type = item["type"]
    del item["type"]
    if _type == "institution":
        code = item["code"]
        del item["code"]
        item["provider_id"] = int(item["provider_id"])
        item["postal_address"]["postcode"] = int(item["postal_address"]["postcode"])
        item["courses"] = {}
        item["contacts"] = []
        item["campuses"] = {}
        institutions[code] = item
        continue
    if _type == "course_campus":
        campus = item["campus"]
        campus = re.sub("^(?:ACT|QLD|NSW|NT|SA|TAS|VIC|WA)\s*-\s*", "", campus)
        courses[item["course"]]["campuses"].append(campus)
        continue

    institution = institutions[item["institution"]]
    del item["institution"]
    if _type == "contact":
        institution["contacts"].append(item)
    if _type == "course":
        code = item["code"]
        del item["code"]
        item["duration"] = int(item["duration"])
        item["campuses"] = []
        courses[code] = institution["courses"][code] = item
    if _type == "campus":
        name = item["name"]
        del item["name"]
        item["postcode"] = int(item["postcode"])
        institution["campuses"][name] = item

json.dump(institutions, open("institutions.json", "w"))
print(json.dumps(institutions))
