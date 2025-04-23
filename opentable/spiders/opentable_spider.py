import scrapy
from lxml import html
from json import loads, dumps
from ..items import RestaurantData, ListingPageData
from scrapy.exceptions import IgnoreRequest
from urllib.parse import quote_plus
import time
import math


class OpentabelSpider(scrapy.Spider):
    name = 'opentable'
    allowed_domains = ['opentable.com', 'google.com']
    start_urls = ['https://www.opentable.com/']

    def parse(self, response):
        dallas_search_url = "https://www.opentable.com/s?latitude=32.86332&longitude=-96.848335&term=restaurants%2C%20Dallas&shouldUseLatLongSearch=false&corrid=7b47c31d-0cfa-4af5-ba82-6d26e5831444&metroId=20&originalTerm=restaurants%2C%20Dallas&queryUnderstandingType=default&sortBy=web_conversion&regionIds[]=60"
        cookies = response.meta.get('curl_cookies')
        yield scrapy.Request(
            url=dallas_search_url,
            callback=self.parse_dallas_search,
            cookies=cookies,
            meta={"use_curl": True}
        )

    def parse_dallas_search(self, response):
        self.check_response(response)
        parser = html.fromstring(response.text)
        json_data_raw = parser.xpath('//script[@type="application/json"]/text()')
        json_data = loads(json_data_raw[0]) if json_data_raw else None
        total_restaurants = json_data.get('windowVariables').get('__INITIAL_STATE__').get('multiSearch').get('totalRestaurantCount')
        restaurants = json_data.get('windowVariables').get('__INITIAL_STATE__').get('multiSearch').get('restaurants')
        for restaurant in restaurants:
            restaurant_name = restaurant.get('name')
            profile_link = restaurant.get('urls').get('profileLink').get('link')
            address_line1, city, state, postcode = self.get_address(restaurant)
            meta = {
                'restaurant_name': restaurant_name,
                'profile_link': profile_link,
                'address_line1': address_line1,
                'city': city,
                'state': state,
                'postcode': postcode,
                "use_curl": True
            }
            listing_page_data = {
                'restaurant_name': restaurant_name,
                'profile_link': profile_link,
                'address_line1': address_line1,
                'city': city,
                'state': state,
                'postcode': postcode, 
            }
            yield ListingPageData(**listing_page_data)
            search_text = f"{restaurant_name}, {address_line1}"
            search_url = f'https://www.google.com/search?hl=en-US&gl=us&q={quote_plus(search_text)}&ludocid=18049663998930109759&lsig=AB86z5WqquafutJDjxyfk5dYIgxY&udm=1&start=00'
            yield scrapy.Request(
                search_url,
                callback=self.parse_google_search,
                meta=meta,
                cookies=response.meta.get('curl_cookies', {}),

                )
            time.sleep(9)
        # if meta.get('pagination'):
        #     return
        # Pagination part
        if total_restaurants > 50:
            total_pages_raw = total_restaurants/50
            total_pages = math.ceil(total_pages_raw)
            pagination_url = "https://www.opentable.com/dapi/fe/gql?optype=query&opname=MultiSearchResults"
            for page_number in range(1, total_pages+1):
                meta = {"pagination": True, "use_curl": True}
                yield scrapy.Request(
                    pagination_url,
                    callback=self.parse_dallas_search_pagingation,
                    meta=meta,
                    method='POST',
                    body=dumps(self.get_payload(page_number)),
                    cookies=response.meta.get('curl_cookies', {}),
                    )
                time.sleep(9)

    def parse_dallas_search_pagingation(self, response):
        self.check_response(response)
        json_data = response.json()
        restaurants = json_data.get('data').get('restaurantSearchV2').get('searchResults').get('restaurants')
        for restaurant in restaurants:
            restaurant_name = restaurant.get('name')
            profile_link = restaurant.get('urls').get('profileLink').get('link')
            address_line1, city, state, postcode = self.get_address(restaurant)
            meta = {
                'restaurant_name': restaurant_name,
                'profile_link': profile_link,
                'address_line1': address_line1,
                'city': city,
                'state': state,
                'postcode': postcode,
                "use_curl": True
            }
            listing_page_data = {
                'restaurant_name': restaurant_name,
                'profile_link': profile_link,
                'address_line1': address_line1,
                'city': city,
                'state': state,
                'postcode': postcode, 
            }
            yield ListingPageData(**listing_page_data)
            search_text = f"{restaurant_name}, {address_line1}"
            search_url = f'https://www.google.com/search?hl=en-US&gl=us&q={quote_plus(search_text)}&ludocid=18049663998930109759&lsig=AB86z5WqquafutJDjxyfk5dYIgxY&udm=1&start=00'
            yield scrapy.Request(
                search_url,
                callback=self.parse_google_search,
                meta=meta,
                cookies=response.meta.get('curl_cookies', {}),

                )
            time.sleep(9)
            # break

    def parse_google_search(self, response):
        self.check_response(response)
        meta = response.meta
        parser = html.fromstring(response.text)
        social_media_link = parser.xpath('//div[@class="wDYxhc"]//g-link/a/@href')
        social_media_link = self.get_social_media_link(parser)
        meta["social_media_link"] = social_media_link
        del meta['use_curl']
        yield RestaurantData(**{
            'restaurant_name': meta.get('restaurant_name'),
            'profile_link': meta.get('profile_link'),
            'address_line1': meta.get('address_line1'),
            'city': meta.get('city'),
            'state': meta.get('state'),
            'postcode': meta.get('postcode'),
            'social_media_link': social_media_link
        })

    def get_social_media_link(self, parser):
        """
        Extract the Instagram link from the parsed HTML.

        Args:
            parser (lxml.html.HtmlElement): The parsed HTML element.

        Returns:
            str: The Instagram link if found, otherwise None.
        """
        social_media_link_raw = parser.xpath('//div[@class="wDYxhc"]//g-link/a/@href')
        if social_media_link_raw:
            social_media_link = ', '.join(social_media_link_raw)
            return social_media_link

    def get_address(self, restaurant):
        """
        Extract address components from the restaurant dictionary.

        Args:
            restaurant (dict): A dictionary containing restaurant information.

        Returns:
            tuple: A tuple containing address_line1, city, state, and postcode.
        """
        address = restaurant.get('address')
        address_line1 = address.get('line1')
        city = address.get('city')
        state = address.get('state')
        postcode = address.get('postCode')
        return address_line1, city, state, postcode

    def check_response(self, response) -> bool:
        """
        Check the HTTP status code of the response and log accordingly and retries.

        Args:
            response: The HTTP response object to check.

        Returns:
            bool: True if the response status is 200.
        """
        if response.status == 200:
            self.logger.info("Response status: 200")
            return True
        else:
            self.logger.warning(f"Bad response ({response.status}). Retrying...")
            raise IgnoreRequest(f"Non-200 response: {response.status}")

    def get_payload(self, page_number):
        """
        Generates the payload for paginated requests.

        Args:
            page_number (int): The page number for which to generate the payload.

        Returns:
            dict: The payload dictionary for the request.
        """
        skipSearchResults = (page_number-1) * 50
        skipCarouselResults = (page_number-1) * 3
        return {
            "operationName": "MultiSearchResults",
            "variables": 
                {
                    "backwardMinutes": 180,
                    "diningType": "ALL",
                    "forwardMinutes": 180,
                    "groupsRids": False,
                    "isAffiliateSearch": False,
                    "isRestrefRequest": False,
                    "maxCarouselResults": 3,
                    "maxSearchResults": 50,
                    "onlyChaseOrVisaRestaurants": False,
                    "onlyJustAdded": False,
                    "onlyVisaRestaurants": False,
                    "onlyWithOffers": False,
                    "skipCarouselResults": skipCarouselResults,
                    "skipSearchResults": skipSearchResults,
                    "sortBy": "WEB_CONVERSION",
                    "withAnytimeAvailability": True,
                    "withCarouselResults": False,
                    "withFallbackToListingMode": False,
                    "latitude": 32.86332,
                    "longitude": -96.848335,
                    "additionalDetailIds": [],
                    "cuisineIds": [],
                    "contextualSearchPromptIds": [],
                    "dinersChoice": [],
                    "date": "2025-04-21",
                    "debug": False,
                    "device": "desktop",
                    "awardTags": [],
                    "experienceTypeIds": [],
                    "intentModifiedTerm": None,
                    "legacyHoodIds": [],
                    "loyaltyRedemptionTiers": [],
                    "macroId": 60,
                    "macroIds": [60],
                    "metroId": 20,
                    "metroIds": [20],
                    "onlyNonEnterpriseCustomers": False,
                    "onlyPop": False,
                    "originalTerm": "restaurants, Dallas",
                    "partySize": 2,
                    "pinnedRid": None,
                    "prices": [],
                    "shouldIncludeDeliveryDetails": True,
                    "shouldIncludeTakeoutDetails": True,
                    "suppressPromotion": False,
                    "tableCategories": [],
                    "tagIds": [],
                    "time": "19:00",
                    "tld": "com",
                    "userLatitude": 9.9406,
                    "userLongitude": 76.2653,
                    "withFacets": False,
                    "withPointRedemptionRewards": False,
                    "countryCode": "US"
                },
                "extensions": 
                {"persistedQuery":
                    {
                        "version": 1,
                        "sha256Hash": "9181e2f0f0f3b8fc8b62f445021d78108c157fb301b424ac4ce038d98a8c1b71"
                    }
                }
                }