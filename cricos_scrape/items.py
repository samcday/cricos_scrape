# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class InstitutionItem(Item):
    type = Field()
    code = Field()
    name = Field()
    tradingName = Field()
    website = Field()
    address = Field()
    contacts = Field()

class CourseItem(Item):
    type = Field()
    institution = Field()
    code = Field()
    name = Field()
    duration = Field()
    level = Field()
