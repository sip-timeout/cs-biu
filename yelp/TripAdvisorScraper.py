from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

TRIP_ADVISOR_REST_URL = 'https://www.tripadvisor.com/Restaurants'
SEARCH_BAR_SELECTOR = '.typeahead_input'
POSTAL_CODE_SELECTOR = '.format_address .locality'
TOPIC_CLASS_SELECTOR = '.ui_tagcloud'


class TripAdvisorScraper:
    def __init__(self):
        self.browser = webdriver.Chrome()

    def get_restaurant_topics(self, rest_name, city, postal_code):
        self.__search_restaurant__(city, rest_name)
        locality_span = self.__wait_by_selector__(POSTAL_CODE_SELECTOR)
        if locality_span:
            if postal_code in locality_span.text:
                return ';'.join(
                    [topic.get_attribute('data-content') for topic in
                     self.browser.find_elements_by_css_selector(TOPIC_CLASS_SELECTOR)[1:]])
        return 'NA'

    def __search_restaurant__(self, city, rest_name):
        self.browser.get(TRIP_ADVISOR_REST_URL)
        search_bar = self.browser.find_element_by_css_selector(SEARCH_BAR_SELECTOR)
        search_bar.clear()
        search_bar.send_keys(','.join([rest_name, city]))
        search_bar.send_keys(Keys.ENTER)

    def __wait_by_selector__(self, css_selector, timeout=10):
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
            return self.browser.find_element_by_css_selector(css_selector)

        except TimeoutException:
            return False
