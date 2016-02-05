# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

import re
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Identity
import phonenumbers


class InstitutionItem(Item):
    type = Field()
    code = Field()
    provider_id = Field()
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


class CourseCampusItem(Item):
    type = Field()
    course = Field()
    campus = Field()


class CampusItem(Item):
    type = Field()
    institution = Field()
    name = Field()
    address_lines = Field()
    suburb = Field()
    postcode = Field()
    phone = Field()
    fax = Field()


def trim(lines):
    return [line.strip() for line in lines]


def trimjoin(lines):
    ret = "".join([line.strip() for line in lines])
    if not len(ret):
        return None
    return ret


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


# TODO: it would be good to log the numbers that fail so we can tweak our
# formatting logic.
# Another TODO: maybe we shouldn't be doing this here. I ran into a number that
# was lacking an area code and was thus not valid. If we were validating and
# formatting numbers at a later stage, we could use additional context such as
# the postal state to infer missing data.
def format_phone(num):
    try:
        num = phonenumbers.parse(num, "AU")
        if not phonenumbers.is_valid_number(num):
            return None
        return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL)
    except:
        return None


def Phone():
    return Compose(trimjoin, format_phone)


class JoiningLoader(ItemLoader):
    default_output_processor = Compose(trimjoin)


class ContactLoader(JoiningLoader):
    default_item_class = ContactItem
    # phone_out = Phone()
    # fax_out = Phone()
    # mobile_out = Phone()


class InstitutionLoader(JoiningLoader):
    default_item_class = InstitutionItem
    postal_address_out = Compose(trim, sanitize_address, parse_address)
