# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

import re
from scrapy.item import Item, Field
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, Join
import phonenumbers


class InstitutionItem(Item):
    type = Field()
    code = Field()
    name = Field()
    tradingName = Field()
    website = Field()
    postal_address = Field()


class ContactItem(Item):
    type = Field()
    institution = Field()
    name = Field()
    title = Field()
    phone = Field()
    fax = Field()
    email = Field()


class CourseItem(Item):
    type = Field()
    institution = Field()
    code = Field()
    name = Field()
    duration = Field()
    level = Field()

class CampusItem(Item):
    type = Field()
    institution = Field()


def trim(lines):
    return [line.strip() for line in lines]


def sanitize_address(lines):
    return [re.sub("[^0-9A-Za-z \./\-,\(\)'&]", "", line) for line in lines]


def parse_address(lines):
    (state, postcode) = re.match("^\s*(.*?)\s*(\d+)\s*$", lines.pop()).groups()
    suburb = lines.pop().strip()
    return {
        "address_lines": lines,
        "suburb": suburb,
        "state": state.strip(),
        "postcode": postcode.strip(),
    }


def format_phone(num):
    num = phonenumbers.parse(num, "AU")
    return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL)


class JoiningLoader(XPathItemLoader):
    default_output_processor = Compose(trim, Join())


class ContactLoader(JoiningLoader):
    default_item_class = ContactItem
    phone_out = Compose(Join(), format_phone)
    fax_out = Compose(Join(), format_phone)
    mobile_out = Compose(Join(), format_phone)


class InstitutionLoader(JoiningLoader):
    default_item_class = InstitutionItem
    postal_address_out = Compose(trim, sanitize_address, parse_address)
