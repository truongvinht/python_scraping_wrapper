import logging
import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

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
            node_list = self.node_selector(self.driver, content_desc)

            # get value
            if len(node_list) > 0 and 'attribute' in content_desc:
                entries = []
                if len(node_list) == 1:
                    content[key] = node_list[0].get_attribute(content_desc['attribute'])
                else:
                    for node in node_list:
                        entries.append(node.get_attribute(content_desc['attribute']))
                    content[key] = entries
            elif len(node_list) > 0:
                content[key] = node_list
        return content
    def node_selector(self, node, content_map):
        logging.info('node_selector: ' + str(content_map))

        # key from json
        KEY_CSS_SELECTOR = 'css_selector'
        KEY_XPATH = 'xpath'
        KEY_SELECTOR = 'selector'
        KEY_PROPERTY = 'property'
        KEY_PROPERTY_FILTER = 'property_filter'
        KEY_INDEX = 'index'

        results = []

        # prevent error by ignoring missing web elements
        try:
            if KEY_CSS_SELECTOR in content_map:
                # css_selector
                selector = content_map[KEY_CSS_SELECTOR]

                if isinstance(selector, str):
                    results.append(node.find_element_by_css_selector(selector))
                    return results
                else:
                    next_node = node.find_element_by_css_selector(selector[KEY_SELECTOR])

                    results.extend(self.node_selector(next_node, selector))
                    return results
            elif KEY_XPATH in content_map:
                # xpath
                selector = content_map[KEY_XPATH]

                if isinstance(selector, str):
                    results.append(node.find_element_by_xpath(selector))
                    return results
                else:
                    if KEY_INDEX in selector:
                        # index search
                        index = selector[KEY_INDEX]
                        next_nodes = node.find_elements_by_xpath(selector[KEY_SELECTOR])

                        if index == -1000:
                            # last index
                            if KEY_CSS_SELECTOR not in selector and KEY_XPATH not in selector:
                                results.append(next_nodes[len(next_nodes)-1])
                                return results


                        if index < 0:
                            # fetch every entry
                            if KEY_PROPERTY in selector:
                                for prop_node in next_nodes:
                                    for attr in prop_node.get_property(selector[KEY_PROPERTY]):
                                        results.append(attr[selector[KEY_PROPERTY_FILTER]])
                            else:
                                results.extend(next_nodes)
                            return results
                        else:
                            # only selected index
                            results.extend(self.node_selector(next_nodes[index], selector))
                            return results
                    else:
                        next_node = node.find_element_by_xpath(selector[KEY_SELECTOR])
                        results.extend(self.node_selector(next_node, selector))
                        return results

        except NoSuchElementException:
            # element not found
            return results
        return results
    def close(self):
        logging.debug('close driver connection')
        self.driver.close()
        self.driver = None
