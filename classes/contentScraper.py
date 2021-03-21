import logging
import json
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

class ContentScraper:
    def __init__(self, url, json_path):
        logging.debug('init ContentScraper')
        with open(json_path) as json_file:
            self.json_page = json.load(json_file)
        # print(self.json_page)
        # target page for scraping
        self.url = url

        # init chrome web driver 
        options = webdriver.chrome.options.Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.url)
    def scraping(self):
        logging.debug('scraping')

        content={}

        time.sleep(2)
        for json_dict in self.json_page:
            # key
            key = json_dict

            # map for all values
            content_desc = self.json_page[key]

            # fetch node for getting content
            node = self.node_selector(self.driver, content_desc)

            # get value
            if node != None and 'attribute' in content_desc:
                content[key] = node.get_attribute(content_desc['attribute'])
        return content
    def node_selector(self, node, content_map):

        if 'css_selector' in content_map:
            selector = content_map['css_selector']

            if isinstance(selector, str):
                return node.find_element_by_css_selector(selector)
            else:
                next_node = node.find_element_by_css_selector(selector["selector"])
                return self.node_selector(next_node, selector)
        elif 'xpath' in content_map:
            selector = content_map['xpath']

            if isinstance(selector, str):
                return node.find_element_by_xpath(selector)
            else:
                next_node = node.find_element_by_xpath(selector["selector"])
                return self.node_selector(next_node, selector)

        return None
    def close(self):
        self.driver.close()
        self.driver = None
