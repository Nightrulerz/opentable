# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RestaurantData(scrapy.Item):
    # define the fields for your item here like:
    restaurant_name = scrapy.Field()
    profile_link = scrapy.Field()
    address_line1 = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    postcode = scrapy.Field()
    social_media_link = scrapy.Field()


class ListingPageData(scrapy.Item):
    restaurant_name = scrapy.Field()
    profile_link = scrapy.Field()
    address_line1 = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    postcode = scrapy.Field()
