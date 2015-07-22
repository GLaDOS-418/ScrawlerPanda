import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions       import DropItem
import re
import os

class MangaPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        yield scrapy.Request(item['imageurl'][0], meta=item)
        pass

    def item_completed(self, results, item, info):
        return item

    def file_path(self, request, response=None, info=None):
        image_guid = request.meta['path']
        image_guid = image_guid + request.meta['thisimage']
        return '%s.jpg' % (image_guid)
