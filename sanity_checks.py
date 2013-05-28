import json

institutions = json.load(open("institutions.json"))
all_campuses = [campus for institution in institutions.values() for campus in institution["campuses"].keys()]

for institution_code, institution in institutions.iteritems():
    for code, course in institution["courses"].iteritems():
        for campus in course["campuses"]:
            if not campus in all_campuses:
                print("Campus %s not found for course %s in institution %s" %
                      (campus, code, institution_code))
