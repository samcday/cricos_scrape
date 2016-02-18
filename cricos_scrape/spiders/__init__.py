# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import re
import json
import urlparse
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request
from cricos_scrape.items import *

stateSelectName = "ctl00$cphDefaultPage$tabContainer$sheetCriteria$institutionSearchCriteria$ddlCourseLocation"
searchTableName = "ctl00_cphDefaultPage_tabContainer_sheetList_" + \
                  "institutionList_gridSearchResults"
institutionTableName = "ctl00_cphDefaultPage_tabContainer_sheetInstitutionDetail"

inst_base = "ctl00_cphDefaultPage_tabContainer_sheetInstitutionDetail_" + \
            "institutionDetail_"

ids = {
    "cricosCode": inst_base + "lblProviderCode",
    "tradingName": inst_base + "lblInstitutionTradingName",
    "name": inst_base + "lblInstitutionName",
    "website": inst_base + "hplInstitutionWebAddress",
    "address": inst_base + "lblInstitutionPostalAddress"
}

institution_selectors = {
    "code": "//span[@id = '%s']/text()" % ids["cricosCode"],
    "name": "//span[@id = '%s']/text()" % ids["name"],
    "tradingName": "//span[@id = '%s']/text()" % ids["tradingName"],
    "website": "//a[@id = '%s']/@href" % ids["website"],
    "address": "//span[@id = '%s']/text()" % ids["address"]
}

course_base = "ctl00_cphDefaultPage_tabContainer_sheetCourseDetail_courseDetail_"
course_selectors = {
    "code": "//span[@id = '%s']/text()" % (course_base + "lblCourseCode"),
    "name": "//span[@id = '%s']/text()" % (course_base + "lblCourseName"),
    "duration": "//span[@id = '%s']/text()" % (course_base + "lblDuration"),
    "level": "//span[@id = '%s']/text()" % (course_base + "lblCourseLevel")
}


def firstXpath(hxs, selector):
    res = hxs.xpath(selector)
    if len(res) > 0:
        return "".join([part.extract() for part in res])
    return ""


def parsePostback(postback):
    m = re.search("__doPostBack\('(.*?)','(.*?)'", postback)
    return (m.group(1), m.group(2))


class CricosSpider(Spider):
    name = "cricos"
    #allowed_domains = ["cricos.deewr.gov.au"] # url has changed
    allowed_domains = ["cricos.education.gov.au"]
    start_urls = [
    	"http://cricos.education.gov.au/Institution/InstitutionSearch.aspx"
        # "http://cricos.deewr.gov.au/Institution/InstitutionSearch.aspx"
    ]

    def parse(self, response):
        """Parses the landing InstitutionSearch.aspx page."""
        hxs = Selector(response)
        locations = hxs.xpath("//select[@name = '%s']/option/@value"
                               % stateSelectName)
        for location in locations[1:]:
            formdata = {
                stateSelectName: location.extract()
            }
            yield FormRequest.from_response(response, formdata=formdata,
                                            callback=self.parse_search)

    def parse_search(self, response):
        hxs = Selector(response)
        hits = hxs.xpath("//table[@id = '%s']/tr[@class = 'gridRow' or @class = 'gridAltItem']/@onclick"
                          % searchTableName)
        for hit in hits:
            (target, argument) = parsePostback(hit.extract())
            formdata = {
                "__EVENTTARGET": target,
                "__EVENTARGUMENT": argument
            }
            yield FormRequest.from_response(response, formdata=formdata,
                                            callback=self.parse_institution,
                                            dont_click=True)
        pages = hxs.xpath("//tr[@class = 'gridPager']//a/@href")
        for page in pages:
            (target, argument) = parsePostback(page.extract())
            formdata = {
                "__EVENTTARGET": target,
                "__EVENTARGUMENT": argument
            }
            yield FormRequest.from_response(response, formdata=formdata,
                                            callback=self.parse_search,
                                            dont_click=True)

    def parse_institution(self, response):
        provider_id = urlparse.parse_qs(urlparse.urlparse(response.request.url).query)["ProviderID"][0]
        hxs = Selector(response)
        l = InstitutionLoader(selector=hxs)
        l.add_value("type", "institution")
        l.add_value("provider_id", provider_id)
        l.add_xpath("code", institution_selectors["code"])
        l.add_xpath("name", institution_selectors["name"])
        l.add_xpath("tradingName", institution_selectors["tradingName"])
        l.add_xpath("website", institution_selectors["website"])
        l.add_xpath("postal_address", institution_selectors["address"])
        item = l.load_item()
        yield item
        contact_selectors = ["//div[@id = 'ctl00_cphDefaultPage_tabContainer_sheetContactDetail_contactDetail_pnlInternationalStudentContactDetails']/table", "//div[@id = 'ctl00_cphDefaultPage_tabContainer_sheetContactDetail_contactDetail_pnlPrincipalExecutiveOfficerDetails']/table"]
        for contact_selector in contact_selectors:
            selector = hxs.xpath(contact_selector)
            if not selector:
                continue
            l = ContactLoader(selector=selector)
            l.add_value("type", "contact")
            l.add_value("institution", item["code"])
            l.add_xpath("name", "tr/td[text()='Name:']/following-sibling::td/text()")
            l.add_xpath("title", "tr/td[text()='Title:']/following-sibling::td/text()")
            l.add_xpath("phone", "tr/td[text()='Phone Number:']/following-sibling::td/text()")
            l.add_xpath("fax", "tr/td[text()='Facsimile Number:']/following-sibling::td/text()")
            l.add_xpath("email", "tr/td[text()='Email Address:']/following-sibling::td/a/text()")
            yield l.load_item()
        meta = {
            "institution": item["code"]
        }
        yield Request(url="http://cricos.deewr.gov.au/Services/GeoService.asmx/GetProviderLocations",
                      method="POST", body=json.dumps({"providerId": provider_id}),
                      headers={"Content-Type": "application/json; charset=utf-8"},
                      meta=meta, callback=self.parse_campus)
        courses = hxs.xpath("//table[@id = '%s']//tr[@class = 'gridRow' or @class = 'gridAltItem']/@onclick" % "ctl00_cphDefaultPage_tabContainer_sheetCourseList_courseList_gridSearchResults")
        for course in courses:
            (target, argument) = parsePostback(course.extract())
            formdata = {
                "__EVENTTARGET": target,
                "__EVENTARGUMENT": argument
            }
            yield FormRequest.from_response(response, formdata=formdata,
                                            callback=self.parse_course,
                                            dont_click=True, meta=meta)

    def parse_course(self, response):
        course_id = urlparse.parse_qs(urlparse.urlparse(response.request.url).query)["CourseID"][0]
        hxs = Selector(response)
        l = JoiningLoader(item=CourseItem(), selector=hxs)
        l.add_value("type", "course")
        l.add_value("institution", response.meta["institution"])
        l.add_xpath("code", course_selectors["code"])
        l.add_xpath("name", course_selectors["name"])
        l.add_xpath("duration", course_selectors["duration"])
        l.add_xpath("level", course_selectors["level"])
        item = l.load_item()
        yield item
        meta = {"course": item["code"]}
        yield Request(url="http://cricos.deewr.gov.au/Services/GeoService.asmx/GetCourseLocations",
                      method="POST", body=json.dumps({"courseId": course_id}),
                      headers={"Content-Type": "application/json; charset=utf-8"},
                      meta=meta, callback=self.parse_course_campuses)

    def parse_course_campuses(self, response):
        items = json.loads(response.body)["d"]
        for item in items:
            course_campus = CourseCampusItem()
            course_campus["type"] = "course_campus"
            course_campus["course"] = response.meta["course"]
            course_campus["campus"] = item["ProviderName"]
            yield course_campus

    def parse_campus(self, response):
        items = json.loads(response.body)["d"]
        phone_processor = Phone()
        for item in items:
            campus = CampusItem()
            campus["type"] = "campus"
            campus["institution"] = response.meta["institution"]
            campus["name"] = item["ProviderName"]
            campus["address_lines"] = [item["AddressLine%d" % i] for i in range(1, 5) if item["AddressLine%d" % i]]
            campus["suburb"] = item["Locality"]
            campus["postcode"] = item["Postcode"]
            campus["phone"] = phone_processor(item["Phone"])
            campus["fax"] = phone_processor(item["Fax"])
            yield campus
