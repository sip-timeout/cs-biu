from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

TRIP_ADVISOR_REST_URL = 'https://www.tripadvisor.com/Restaurants'
SEARCH_BAR_SELECTOR = '#mainSearch'
SEARCH_LOC_SELECTOR = '#GEO_SCOPED_SEARCH_INPUT'
POSTAL_CODE_SELECTOR = '.format_address .locality'
TOPIC_CLASS_SELECTOR = '.ui_tagcloud'
SEARCH_BUTTON_SELECTOR = '#taplc_masthead_search_0'
SEARCH_RESULT_IMG_SELECTOR = '.photo_image'


class TripAdvisorScraper:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.counter = 0

    def get_restaurant_topics(self, rest_name, city, postal_code):
        topics = 'NA'
        self.counter += 1

        if self.counter % 50 == 0:
            self.browser.close()
            self.browser = webdriver.Chrome()
            time.sleep(60)
        try:
            self.__search_restaurant__(city, rest_name)
            self.browser.switch_to.window(self.browser.window_handles[-1])
            locality_span = self.__wait_by_selector__(POSTAL_CODE_SELECTOR)
            if locality_span:
                if postal_code in locality_span.text:
                    topics = ';'.join(
                        [topic.get_attribute('data-content') for topic in
                         self.browser.find_elements_by_css_selector(TOPIC_CLASS_SELECTOR)[1:]])
            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[0])
        except Exception as ex:
            print ex
        return topics

    def __search_restaurant__(self, city, rest_name):
        self.browser.get(TRIP_ADVISOR_REST_URL)
        self.browser.maximize_window()

        self.__wait_by_selector__(SEARCH_BUTTON_SELECTOR)
        self.browser.find_element_by_css_selector(SEARCH_BUTTON_SELECTOR).click()

        time.sleep(1)

        search_input = self.browser.find_element_by_css_selector(SEARCH_BAR_SELECTOR)
        search_input.clear()
        search_input.send_keys(rest_name)

        location_input = self.browser.find_element_by_css_selector(SEARCH_LOC_SELECTOR)
        location_input.send_keys(city)

        search_input.send_keys(Keys.ENTER)

        self.browser.find_element_by_css_selector(SEARCH_RESULT_IMG_SELECTOR).click()

    def __wait_by_selector__(self, css_selector, timeout=10):
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
            return self.browser.find_element_by_css_selector(css_selector)

        except TimeoutException:
            return False
