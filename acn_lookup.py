import os
import json
import logging
from suds.client import Client

logging.getLogger().setLevel(logging.INFO)
abr_guid = os.environ["ABR_GUID"]

cli = Client("http://abr.business.gov.au/abrxmlsearch/abrxmlsearch.asmx?wsdl")

try:
    acns = json.load(open("acns.json"))
except IOError:
    acns = {}
except ValueError:
    acns = {}


def write_acn_file():
    json.dump(acns, open("acns.json", "w"))


def lookup_acn(abn):
    if abn in acns:
        return acns[abn]
    logging.info("Looking up ACN for %s", abn)
    res = cli.service.ABRSearchByABN(abn, "N", abr_guid).response
    acn = False
    if "businessEntity" in res and "ASICNumber" in res.businessEntity:
        acn = res.businessEntity.ASICNumber
    acns[abn] = acn
    return acn


abns = [item["abn"] for item in json.load(open("abns.json")).values()
        if "abn" in item]

for abn in abns:
    try:
        lookup_acn(abn)
    except KeyboardInterrupt:
        break
    except Exception as e:
        write_acn_file()
        raise e

write_acn_file()
