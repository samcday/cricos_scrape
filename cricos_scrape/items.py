# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Join


class InstitutionItem(Item):
    type = Field()
    code = Field()
    name = Field()
    tradingName = Field()
    website = Field()
    address = Field()


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


class JoiningLoader(XPathItemLoader):
    default_output_processor = Join()
