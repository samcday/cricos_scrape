# Scrapy settings for cricos_scrape project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'cricos_scrape'

SPIDER_MODULES = ['cricos_scrape.spiders']
NEWSPIDER_MODULE = 'cricos_scrape.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cricos_scrape (+http://www.yourdomain.com)'
