import os
import json
import sys
from suds.client import Client

abr_guid = os.environ["ABR_GUID"]

cli = Client("http://abr.business.gov.au/abrxmlsearch/abrxmlsearch.asmx?wsdl")

try:
    abns = json.load(open("abns.json"))
except IOError:
    abns = {}

state_acronyms = {
    "Australian Capital Territory": "ACT",
    "New South Wales": "NSW",
    "Northern Territory": "NT",
    "Queensland": "QLD",
    "South Australia": "SA",
    "Tasmania": "TAS",
    "Victoria": "VIC",
    "Western Australia": "WA"
}


def write_abn_file():
    json.dump(abns, open("abns.json", "w"))


def lookup_abn(name, state):
    if name in abns:
        return abns[name]
    req = cli.factory.create("ExternalRequestNameSearch")
    req.name = name
    req.filters.nameType.legalName = "Y"
    req.filters.stateCode[state] = "Y"
    resp = cli.service.ABRSearchByName(req, abr_guid).response
    results = resp.searchResultsList
    if not results.numberOfRecords:
        return None
    result = results.searchResultsRecord[0]
    if result.mainName.score != 100:
        return None
    abn = result.ABN[0].identifierValue
    abns[name] = abn
    return abn


institutions = json.load(open("institutions.json"))

for cricos, institution in institutions.iteritems():
    try:
        state = state_acronyms[institution["postal_address"]["state"]]
        print("%s: %s" % (institution["name"], lookup_abn(institution["name"], state)))
    except KeyboardInterrupt:
        write_abn_file()
        sys.exit()

write_abn_file()
