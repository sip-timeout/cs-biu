from lxml import etree
from lxml.cssselect import CSSSelector
from selenium import webdriver
import time
import json

browser = webdriver.Chrome()


def extract_pois(rest_page):

    def get_topics(url):
        browser.get(url)
        browser.execute_script('scroll(0,document.body.scrollHeight)')
        topics = []
        topic_elements = browser.find_elements_by_css_selector('span.ui_tagcloud')
        for topic in topic_elements:
            topics.append(topic.get_attribute('data-content'))

        return topics[1:]


    browser.get(rest_page)
    browser.execute_script('scroll(0,document.body.scrollHeight)')
    time.sleep(3)
    html = browser.find_element_by_tag_name('body').get_attribute('outerHTML')
    parsedHtml = etree.HTML(html)
    pois = parsedHtml.cssselect('.listing')

    poi_objects = []
    for poi in pois:
        poi_obj = {}

        link = poi.cssselect('.photo_link')[0]
        poi_obj['url'] = 'http://www.tripadvisor.com' + link.attrib['href']

        img = poi.cssselect('.photo_image')[0]
        poi_obj['name'] = img.attrib['alt']
        poi_obj['img'] = img.attrib['src']

        # print poi.attrib['outerHTML']
        review = poi.cssselect('.ui_bubble_rating')[0]
        poi_obj['rating'] = review.attrib['alt'][:review.attrib['alt'].find(' ')]

        cuisines = poi.cssselect('.cuisine')
        poi_obj['cuisines'] = [cuisine.text for cuisine in cuisines]

        poi_obj['topics'] = get_topics(poi_obj['url'])

        poi_objects.append(poi_obj)

    return poi_objects


def main():
    pois = extract_pois('https://www.tripadvisor.com/Restaurants-g294265-Singapore.html')
    with open('pois.json', 'w') as pois_file:
        json.dump(pois, pois_file, sort_keys=True, indent=4, separators=(',', ': '))
    browser.close()


if __name__ == "__main__":
    main()
