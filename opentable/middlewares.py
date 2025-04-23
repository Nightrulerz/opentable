# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from curl_cffi import requests
from scrapy.http import HtmlResponse
from .useragents import user_agents
from random import choice, uniform

class CurlCFFIMiddleware:
    def process_request(self, request, spider):
        use_curl = request.meta.get('use_curl')
        global_use_curl = getattr(spider.settings, "getbool", lambda x, y=None: y)("USE_CURL_CFFI", True)
        if use_curl is None:
            use_curl = global_use_curl
        if use_curl:
            headers = self.get_headers(url=request.url)
            if request.method == 'POST':
                r = requests.post(
                    request.url,
                    headers=headers,
                    impersonate="chrome123",
                    data=request.body,
                    timeout=20,
                )
            else:
                r = requests.get(
                    request.url,
                    allow_redirects=True,
                    headers=headers,
                    impersonate="chrome123",
                    timeout=20,
                )
            cookies = dict(r.cookies)
            response = HtmlResponse(
                url=request.url,
                status=r.status_code,
                body=r.content,
                request=request
            )
            response.meta['curl_cookies'] = cookies
            return response
        return None

    def get_headers(self, url=None) -> dict:
        """
        Construct and return headers for the request.

        Args:
            referer (str): The referer URL to include in the headers. Default to homepage.

        Returns:
            dict: A dictionary containing HTTP request headers.
        """
        if "www.google.com/search" in url:
            return {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-GB,en;q=0.9',
                    'downlink': '10',
                    'priority': 'u=0, i',
                    'referer': 'https://www.google.com/',
                    'rtt': '50',
                    'sec-ch-prefers-color-scheme': 'light',
                    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                    'sec-ch-ua-arch': '"x86"',
                    'sec-ch-ua-bitness': '"64"',
                    'sec-ch-ua-form-factors': '"Desktop"',
                    'sec-ch-ua-full-version': '"135.0.7049.95"',
                    'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.95", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.95"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-platform': '"Linux"',
                    'sec-ch-ua-platform-version': '"6.8.0"',
                    'sec-ch-ua-wow64': '?0',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                    'x-browser-channel': 'stable',
                    'x-browser-copyright': 'Copyright 2025 Google LLC. All rights reserved.',
                    'x-browser-validation': '5RoN3vy0OGjriXSTe0RgzBFbV+U=',
                    'x-browser-year': '2025',
                            }
        if "/dapi/fe/gql" in url:
            return {
                'accept': '*/*',
                'accept-language': 'en-GB,en;q=0.5',
                'content-type': 'application/json',
                'origin': 'https://www.opentable.com',
                'ot-page-group': 'search',
                'ot-page-type': 'multi-search',
                'priority': 'u=1, i',
                'referer': 'https://www.opentable.com/s?latitude=32.86332&longitude=-96.848335&term=restaurants%2C%20Dallas&shouldUseLatLongSearch=false&corrid=a20ede84-316a-49c1-bf55-237c98331d2f&metroId=20&originalTerm=restaurants%2C%20Dallas&queryUnderstandingType=default&sortBy=web_conversion&regionIds[]=60',
                'sec-ch-ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'x-csrf-token': 'e9d2af51-631b-4b44-a8bd-8dff83fc7bbd',
                'x-query-timeout': '11779',
                }
        else:
            return {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'en-GB,en;q=0.5',
                'cache-control': 'max-age=0',
                'priority': 'u=0, i',
                'referer': 'https://www.opentable.com/',
                'sec-ch-ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'sec-gpc': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': self.get_user_agent()
                }

    def get_user_agent(self) -> str:
        """
        Get useragent for the request.

        Returns:
            str: A random user-agent string from the user_agents list.
        """
        return choice(user_agents)

class OpentableSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class OpentableDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
