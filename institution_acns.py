import json

institutions = json.load(open("institutions.json"))
abns = json.load(open("abns.json"))
acns = json.load(open("acns.json"))

for cricos, institution in institutions.iteritems():
    abn = abns[institution["name"]]
    if "abn" in abn:
        abn = abn["abn"]
        institution["abn"] = abn
        institution["acn"] = acns[abn]

json.dump(institutions, open("institutions.json", "w"))
