import scrapy
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class OlxItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Area = scrapy.Field()
    City = scrapy.Field()
    District = scrapy.Field()
    ADNumber = scrapy.Field()
    Phone_Num = scrapy.Field()

class Olx_ua(scrapy.Spider):
    name = "olx_ua_products"
    START_URL = 'https://www.olx.ua'
    HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/57.0.2987.133 Safari/537.36"}
    def start_requests(self):
        category_links = ['https://www.olx.ua/detskiy-mir/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/nedvizhimost/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/transport/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/zhivotnye/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/dom-i-sad/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/elektronika/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/uslugi/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/moda-i-stil/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/hobbi-otdyh-i-sport/?search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/otdam-darom/?search%5Bfilter_float_price%3Afrom%5D=free&search%5Bprivate_business%5D=private'
                          'https://www.olx.ua/obmen-barter/?search%5Bfilter_float_price%3Afrom%5D=exchange&search%5Bprivate_business%5D=private'
                          ]
        for category in category_links:
            yield scrapy.Request(url=category, callback=self.click_page_number, dont_filter=True, headers=self.HEADER)

    def click_page_number(self, response):
        PageCount = response.xpath('//div[contains(@class, "pager")]'
                                   '/span[contains(@class, "item")]/a/span')[-1].extract()
        PageCount = int(re.search('(\d+)', PageCount, re.DOTALL).group(1))
        for i in range(1, PageCount):
            url = response.url + '&page=' + str(i)
            yield scrapy.Request(url=url, callback=self.goto_detail, dont_filter=True, headers= self.HEADER)

    #goto Detail link
    def goto_detail(self, response):
        detail_link = response.xpath('//div[@class="wrapper"]//table/tbody/tr[@class="wrap"]/td/table/tbody/tr/td[@valign="top"]/div/h3/a/@href').extract()
        for det_url in detail_link:
            if 'https' in det_url:
                goto_detail_link = det_url
            else:
                goto_detail_link = self.START_URL + det_url
            yield  scrapy.Request(url=goto_detail_link, callback=self.get_address_phone, dont_filter=True, headers=self.HEADER)

    #get_values
    def get_address_phone(self, response):
        item = OlxItem();
        address = response.xpath('//div[@id="offer_active"]//div[@id="offerdescription"]'
                                 '/div[@class="offer-titlebox"]/div[@class="offer-titlebox__details"]/a/strong/text()')[0].extract()
        adNum = response.xpath('//div[@id="offer_active"]//div[@id="offerdescription"]'
                                 '/div[@class="offer-titlebox"]/div[@class="offer-titlebox__details"]/em/small/text()')[0].extract()
        array = address.split(',')

        area = array[0].strip()
        item["Area"] = area
        if len(array) > 2:
            district = array[2].strip()
            item["District"] = district
        if len(array) > 1:
            city = array[1].strip()
            item["City"] = city

        array = adNum.split(':')
        adNum = int(array[1].strip())
        item["ADNumber"] = adNum

        driver = webdriver.Firefox()

        driver.get(response.url)
        contact_button = driver.find_element_by_xpath("//div[contains(@class, 'contact-button')]"
                                                      "//strong[@class='xx-large']")

        contact_button.click()
        while True:
            phone_num = driver.find_element_by_xpath("//div[contains(@class, 'contact-button')]//strong[@class='xx-large']").text
            if 'x' in phone_num:
                continue
            if phone_num.startswith('+'):
                phone_num=phone_num[1:]
            if phone_num.startswith('0'):
                phone_num='38'+phone_num
            item['Phone_Num'] = int(phone_num.replace(' ', ''))
            break
        yield item