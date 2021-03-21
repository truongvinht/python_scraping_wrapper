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
        logging.debug('node_selector: ' + str(content_map))

        # key from json
        KEY_CSS_SELECTOR = 'css_selector'
        KEY_XPATH = 'xpath'
        KEY_SELECTOR = 'selector'

        # prevent error by ignoring missing web elements
        try:
            if KEY_CSS_SELECTOR in content_map:
                # css_selector
                selector = content_map[KEY_CSS_SELECTOR]

                if isinstance(selector, str):
                    return node.find_element_by_css_selector(selector)
                else:
                    next_node = node.find_element_by_css_selector(selector[KEY_SELECTOR])
                    return self.node_selector(next_node, selector)
            elif KEY_XPATH in content_map:
                # xpath
                selector = content_map[KEY_XPATH]

                if isinstance(selector, str):
                    return node.find_element_by_xpath(selector)
                else:
                    next_node = node.find_element_by_xpath(selector[KEY_SELECTOR])
                    return self.node_selector(next_node, selector)
        except NoSuchElementException:
            # element not found
            return None
        return None
    def close(self):
        logging.debug('close driver connection')
        self.driver.close()
        self.driver = None
