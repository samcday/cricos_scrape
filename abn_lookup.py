import os
import json
import sys
import logging
import re
from suds.client import Client

abr_guid = os.environ["ABR_GUID"]

cli = Client("http://abr.business.gov.au/abrxmlsearch/abrxmlsearch.asmx?wsdl")

logging.getLogger().setLevel(logging.INFO)

try:
    abns = json.load(open("abns.json"))
except IOError:
    abns = {}
except ValueError:
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

regexes = [
    re.compile("(.*?)\s*\([^\(\)]*?\)\s*$"),  # Acronym suffix
    re.compile("^The Council of (.*)", re.IGNORECASE)  # The Council of <Foo>
]


def write_abn_file():
    json.dump(abns, open("abns.json", "w"))


def lookup_abn(name):
    if name in abns:
        existing = abns[name]
        if "abn" in existing:
            return existing["abn"]
        if "see" in existing:
            return lookup_abn(existing["see"])
        if "missing" in existing:
            return None
    logging.info("Looking up ABN for %s", name)
    req = cli.factory.create("ExternalRequestNameSearch")
    req.name = name
    req.filters.nameType.legalName = "Y"
    for state, dummy in req.filters.stateCode:
        req.filters.stateCode[state] = "Y"
    resp = cli.service.ABRSearchByName(req, abr_guid).response
    if "searchResultsList" in resp:
        results = resp.searchResultsList
        if results.numberOfRecords:
            result = results.searchResultsRecord[0]
            match = ("mainName" in result and result.mainName.score == 100) or \
                    ("legalName" in result and result.legalName.score == 100)
            if match:
                abn = result.ABN[0].identifierValue
                abns[name] = {"abn": abn}
                return abn

    # We didn't get a 100% score match
    # See if any of our cleaning regexes will help.
    for regex in regexes:
        match = re.match(regex, name)
        if match is not None:
            new_name = match.group(1)
            attempt = lookup_abn(new_name)
            if attempt is not None:
                abns[name] = {"see": new_name}
                return attempt
    abns[name] = {"missing": True}
    return None

institutions = json.load(open("institutions.json"))

missing_abns = []
try:
    for cricos, institution in institutions.iteritems():
        try:
            abn = lookup_abn(institution["name"])
            if abn is None:
                missing_abns.append(institution["name"])
            # logging.info("Found ABN %s for %s", abn, institution["name"])
        except KeyboardInterrupt:
            write_abn_file()
            sys.exit()
except Exception as e:
    print("Unhandled exception!")
    write_abn_file()
    raise e

write_abn_file()

print "Missing ABNs:"
print missing_abns
print "Total: %d" % len(missing_abns)
