# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from cricos_scrape.items import InstitutionItem

stateSelectName = "ctl00$cphDefaultPage$tabContainer$sheetCriteria$institutionSearchCriteria$ddlCourseLocation"
searchTableName = "ctl00_cphDefaultPage_tabContainer_sheetList_" + \
                  "institutionList_gridSearchResults"
institutionTableName = "ctl00_cphDefaultPage_tabContainer_sheetInstitutionDetail"

inst_fields = {
    "base": "ctl00_cphDefaultPage_tabContainer_sheetInstitutionDetail"
}

details_base = "ctl00_cphDefaultPage_tabContainer_sheetInstitutionDetail_" + \
               "institutionDetail_"

ids = {
    "cricosCode": details_base + "lblProviderCode",
    "tradingName": details_base + "lblInstitutionTradingName",
    "name": details_base + "lblInstitutionName",
    "website": details_base + "hplInstitutionWebAddress"
}

institution_selectors = {
    "code": "//span[@id = '%s']/text()" % ids["cricosCode"],
    "name": "//span[@id = '%s']/text()" % ids["name"],
    "tradingName": "//span[@id = '%s']/text()" % ids["tradingName"],
    "website": "//a[@id = '%s']/@href" % ids["website"],
}


def firstXpath(hxs, selector):
    res = hxs.select(selector)
    if len(res) > 0:
        return res[0].extract()
    return ""


def parsePostback(postback):
    m = re.search("__doPostBack\('(.*?)','(.*?)'", postback)
    return (m.group(1), m.group(2))


class CricosSpider(BaseSpider):
    name = "cricos"
    allowed_domains = ["cricos.deewr.gov.au"]
    start_urls = [
        "http://cricos.deewr.gov.au/Institution/InstitutionSearch.aspx"
    ]

    def parse(self, response):
        """Parses the landing InstitutionSearch.aspx page."""
        hxs = HtmlXPathSelector(response)
        locations = hxs.select("//select[@name = '%s']/option/@value"
                               % stateSelectName)
        requests = []
        for location in locations:
            formdata = {
                stateSelectName: location.extract()
            }
            requests.append(FormRequest.from_response(response,
                            formdata=formdata, callback=self.parse_search))
        # return requests
        return [requests.pop()]

    def parse_search(self, response):
        hxs = HtmlXPathSelector(response)
        requests = []
        hits = hxs.select("//table[@id = '%s']/tr[@class = 'gridRow' or @class = 'gridAltItem']/@onclick"
                          % searchTableName)
        for hit in hits:
            (target, argument) = parsePostback(hit.extract())
            formdata = {
                "__EVENTTARGET": target,
                "__EVENTARGUMENT": argument
            }
            requests.append(FormRequest.from_response(response,
                            formdata=formdata, callback=self.parse_institution,
                            dont_click=True))
        pages = hxs.select("//tr[@class = 'gridPager']//a/@href")
        for page in pages:
            (target, argument) = parsePostback(page.extract())
            formdata = {
                "__EVENTTARGET": target,
                "__EVENTARGUMENT": argument
            }
            requests.append(FormRequest.from_response(response,
                            formdata=formdata, callback=self.parse_search,
                            dont_click=True))
        return requests

    def parse_institution(self, response):
        hxs = HtmlXPathSelector(response)
        item = InstitutionItem()
        item["code"] = firstXpath(hxs, institution_selectors["code"])
        item["name"] = firstXpath(hxs, institution_selectors["name"])
        item["tradingName"] = firstXpath(hxs,
                                         institution_selectors["tradingName"])
        item["website"] = firstXpath(hxs, institution_selectors["website"])
        return item
