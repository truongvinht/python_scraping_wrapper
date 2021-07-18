import logging
import json
import time
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

# Scraping Tool
class ContentScraper:
    # init with default download location
    def __init__(self, folder = "./"):
        logging.debug('init ContentScraper')

        # json configuration map for scraping
        self.json_page = None

        # init chrome web driver 
        options = webdriver.chrome.options.Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("prefs", {
            "download.default_directory": folder,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        self.driver = webdriver.Chrome(options=options)

    # load json file for scraping
    def loadJson(self, json_path):
        with open(json_path) as json_file:
            self.json_page = json.load(json_file)

    # load target page
    def load(self, url):
        # target page for scraping
        self.driver.get(url)

    # fill in user name, password and continue
    def site_login(self, userField, user, pwdField, pwd, submitField):
        self.driver.find_element_by_xpath(userField).send_keys(user)
        self.driver.find_element_by_xpath(pwdField).send_keys(pwd)

        self.click_xpath(submitField)
    # wait and do nothing
    def wait(self, duration):
        time.sleep(duration)
    # remove all cookies
    def clear_cookies(self):
        self.driver.delete_all_cookies()
    
    # execute click event on element 
    def click_xpath(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()

    # create a screenshot with width and size
    def create_screenshot(self, name, width, height):
        self.driver.set_window_size(width, height)
        time.sleep(2)
        self.driver.save_screenshot(name)

    # save page source as file
    def save_webpage(self, filename):
        filehandle = open(filename, 'w')
        filehandle.write(self.page_source())
        filehandle.close()
    
    # download file
    def download_file_as(self, url, name):
        self.load(url)
        r = requests.get(url)
        with open(name, 'wb') as outfile:
            outfile.write(r.content)

    # page source
    def page_source(self):
        return self.driver.page_source
    

    # scrape page based on configured json
    def scraping(self):
        logging.debug('scraping: ' + self.driver.current_url)

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

        logging.info('scraping completed!')
        return content
    
    # process content
    def node_selector(self, node, content_map):
        logging.debug('node_selector: ' + str(content_map))

        # key from json
        KEY_CSS_SELECTOR = 'css_selector'
        KEY_XPATH = 'xpath'
        KEY_SELECTOR = 'selector'
        KEY_PROPERTY = 'property'
        KEY_PROPERTY_FILTER = 'property_filter'
        KEY_INDEX = 'index'
        KEY_SKIPPING = 'skipping_key'

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
                                        if attr[selector[KEY_PROPERTY_FILTER]] == '':
                                            logging.debug('skip empty')
                                        else:
                                            if KEY_SKIPPING in selector and selector[KEY_SKIPPING] in attr[selector[KEY_PROPERTY_FILTER]]:
                                                logging.debug('skip: ' + attr[selector[KEY_PROPERTY_FILTER]])
                                            else:
                                                results.append(attr[selector[KEY_PROPERTY_FILTER]])
                            else:
                                logging.error('key is not inside')
                                results.extend(next_nodes)
                            return results
                        else:
                            # only selected index
                            try:
                                results.extend(self.node_selector(next_nodes[index], selector))
                                return results
                            except IndexError:
                                logging.error('IndexError: list index out of range')
                                logging.debug('nodes: ' + str(next_nodes) + ', index: ' + str(index)+', selector: ' + str(selector))
                                logging.debug('node: ' + str(node) + ', results: ' + str(results))
                                return []
                    else:
                        next_node = node.find_element_by_xpath(selector[KEY_SELECTOR])
                        results.extend(self.node_selector(next_node, selector))
                        return results

        except NoSuchElementException:
            # element not found
            return results
        return results
    
    # close driver connection
    def close(self):
        logging.debug('close driver connection')
        self.driver.close()
        self.driver = None
