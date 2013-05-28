import json
import re
import phonenumbers
data = json.load(open("result.json"))

institutions = {}
courses = {}

state_area_codes = {
    "Australian Capital Territory": "02",
    "New South Wales": "02",
    "Northern Territory": "08",
    "Queensland": "07",
    "South Australia": "08",
    "Tasmania": "03",
    "Victoria": "03",
    "Western Australia": "08"
}


def format_phone(rawnum, institution):
    if rawnum is None:
        return None
    cleannum = re.sub("[^0-9]", "", rawnum)
    try:
        num = phonenumbers.parse(rawnum, "AU")
        # If parse failed and number is exactly 8 digits, it's probably just
        # missing area code.
        if not phonenumbers.is_valid_number(num) and len(cleannum) == 8:
            area_code = state_area_codes[institution["postal_address"]["state"]]
            num = phonenumbers.parse(area_code + rawnum, "AU")
        if not phonenumbers.is_valid_number(num):
            print("Error parsing number %s" % rawnum)
            return None
        return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL)
    except:
        print("Error parsing number %s" % rawnum)
        return None


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
        item["phone"] = format_phone(item["phone"], institution)
        item["fax"] = format_phone(item["fax"], institution)
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
        item["phone"] = format_phone(item["phone"], institution)
        item["fax"] = format_phone(item["fax"], institution)
        institution["campuses"][name] = item

json.dump(institutions, open("institutions.json", "w"))
print(json.dumps(institutions))
