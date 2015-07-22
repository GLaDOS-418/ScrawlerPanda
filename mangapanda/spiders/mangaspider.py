from scrapy.spiders         import CrawlSpider, Rule
from scrapy.linkextractors  import LinkExtractor
from scrapy.http            import Request
from urlparse               import urljoin
from lxml                   import html
from mangapanda.items       import MangaItem

import requests
import re
import scrapy

class MangaSpider(CrawlSpider):

    name         = "mangapanda"
    allowed_domains    = ["mangapanda.com"]
    start_urls    = ["http://www.mangapanda.com/alphabetical"]

    manga = ''
    manganumber=''
    nextlinkpattern = "/[0-9]+$"
    pattern1 = "/[\d]+$"
    pattern2 = ""
    rules = [
                Rule(LinkExtractor(allow=[pattern1, pattern2] , restrict_xpaths=('//*[@id = "imgholder"]/a', )), callback='parse_start_url', follow=True),
            ]

    def __init__(self, manganame='', *a, **kw):

        super(MangaSpider, self).__init__(*a, **kw)
        mangalist = []
        if(manganame):
            tree = html.fromstring(requests.get(self.start_urls[0]).text)
            mangalist = tree.xpath('//*[@id="wrapper_body"]/div/div[@class="series_col"]/div[@class="series_alpha"]/ul/li/a[re:match(text(), "{0}", "i")]/text()'.format(manganame), namespaces = {"re": "http://exslt.org/regular-expressions"})
            print mangalist
            print "enter your choice (0-based index): "
            i = int(raw_input())
            specific = tree.xpath('//*[@id="wrapper_body"]/div/div[@class="series_col"]/div[@class="series_alpha"]/ul/li/a[re:match(text(),"{0}", "i")]/@href'.format(mangalist[i]) ,namespaces = {"re": "http://exslt.org/regular-expressions"})
            self.manga= mangalist[i]

            self.start_urls[0] = urljoin(self.start_urls[0],specific[0])

            nextpagetree = html.fromstring(requests.get(self.start_urls[0]).text)
            latestmanga = nextpagetree.xpath('//*[@id="listing"]//tr[last()]/td')

            print "latest manga: " + latestmanga[0].xpath("a/text()")[0] + "\tdate released(mm-dd-yyyy): "+latestmanga[1].xpath("text()")[0]+"\nenter the required manga number: "
            i = str(raw_input())

            self.manganumber = i
            self.pattern1 = '/' + i + self.pattern1
            self.pattern2 = '/' + i + '$'

            MangaSpider.rules = rules = [ Rule(LinkExtractor(allow=[self.pattern1, self.pattern2] , restrict_xpaths=('//*[@id = "imgholder"]/a', )), callback='parse_start_url', follow=True), ]
            super(MangaSpider, self)._compile_rules()

            i='/'+ i +'$'
            i=re.compile(i)
            x=nextpagetree.xpath('//*[@id="listing"]//tr/td/a/@href')
            for y in x:
                if re.search(i,y):
                    requiredmanga = y
                    break
                pass
            self.start_urls[0] = urljoin(self.start_urls[0],requiredmanga)
        pass


    def parse_start_url(self, response):
        hxs = scrapy.Selector(response)
        img = hxs.xpath('//*[@id="imgholder"]/a')

        item = MangaItem()
        item["path"] = self.manga + '/' + self.manganumber +'/'
        item["thisimage"] = (re.search("[\d]+$",response.url).group() if re.search("htt(p|ps)://[a-zA-z\.]+/[a-zA-Z0-9\.#-]+/[\d]+/[\d]+$",response.url) else "1")
        item["imageurl"] = img.xpath('img/@src').extract()
        yield item
        pass
