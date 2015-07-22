from scrapy.item import Item, Field

class MangaItem(Item):

    thisimage = Field()
    path = Field()
    imageurl = Field()
