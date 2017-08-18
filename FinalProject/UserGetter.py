from _threading_local import local

from pip import locations
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, \
    ElementNotVisibleException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from lxml import etree
from lxml.cssselect import CSSSelector

import time
import re
import json
import urllib2

users_map = {}
restaurants = {}
hotels = {}
attractions = {}

browser = webdriver.Chrome()


def close_popup_if_exists():
    if wait_by_selector('.ui_close_x', 2):
        close_ui = browser.find_elements_by_class_name('ui_close_x')
        for close_ui in close_ui:
            close_ui.click()


def wait_by_selector(css_selector, timeout=10):
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        return True

    except TimeoutException:
        return False


def init_page(trip_url):
    global first_page
    first_page = 1
    browser.maximize_window()
    browser.get(trip_url)
    # elem = browser.find_element_by_tag_name('a')
    # elem.click()
    wait_by_selector('.member_info')


def getRating(rat):
    cls = rat.get_attribute('class')
    if 'bubble' in cls:
        idx = cls.rfind('_') + 1
        rating = cls[idx:]
        if len(rating)<2:
            rating+='0'
        return rating[0] + '.' + rating[1]
    else:
        return ''

def extract_page_users(poi_name):
    global first_page

    def extractUserPreview(userName):
        global users_map
        user = {}

        user["userName"] = userName
        user["name"] = browser.find_element_by_css_selector("h3.username").text

        try:
            user["level"] = browser.find_element_by_css_selector(".badgeinfo span").text
        except NoSuchElementException:
            pass

        for desc in browser.find_elements_by_css_selector(".memberdescriptionReviewEnhancements li"):
            try:
                descTXT = str(desc.text).lower()
            except UnicodeEncodeError:
                browser.find_element_by_class_name('ui_close_x').click()
                return None

            if descTXT.find('since') > -1:
                user["joinDate"] = descTXT.split(' ')[-1]
            if descTXT.find('from') > -1:
                user["location"] = descTXT[descTXT.find('from') + 5:]
            if descTXT.find('man ') > -1:
                user["gender"] = "M"
            if descTXT.find('woman ') > -1:
                user["gender"] = "F"
            if re.match('[0-9]{2}-[0-9]{2}', descTXT):
                st, end = re.match('[0-9]{2}-[0-9]{2}', descTXT).regs[0]
                user["age"] = descTXT[st:end + 1]

        revDist = []
        for revCount in browser.find_elements_by_css_selector(".barchartmemoverlay .row .numbersText"):
            revDist.append(str(revCount.text).strip('(').strip(')'))

        user["reviewDist"] = revDist

        user['restName'] = poi_name

        def getCountValue(countHTML):
            endidx = countHTML.find(' ')
            return countHTML[0:endidx]

        for count in browser.find_elements_by_css_selector(
                ".countsReviewEnhancementsItem .badgeTextReviewEnhancements"):
            countHtml = str(count.get_attribute("innerHTML"))
            if countHtml.find("Contributions") > -1:
                user["contrib"] = getCountValue(countHtml)
            if countHtml.find("Helpful") > -1:
                user["helpful"] = getCountValue(countHtml)
            if countHtml.find("Cities") > -1:
                user["cityCount"] = getCountValue(countHtml)

        users_map[userName] = user
        return user

    def getReviewContent(cont):
        return cont.text


    elems = browser.find_elements_by_class_name('member_info')

    temp_user_map = {}
    for i in range(1 - first_page, 11 - first_page):

        elem = elems[i]
        try:
            elem.click()
        except:
            print 'shit shit shit'
            close_popup_if_exists()
            continue

        member_info_html = elem.get_attribute('outerHTML')
        parsed_html = etree.HTML(member_info_html)
        user_img_url = parsed_html.cssselect('img')[0].attrib['src']

        if wait_by_selector('.memberOverlay', 3):
            elem = browser.find_element_by_css_selector('.memberOverlay a')
        else:
            close_elems = browser.find_elements_by_class_name('ui_close_x')
            if len(close_elems) > 0:
                close_elems[0].click()
            continue

        user_object = extractUserPreview(elem.get_attribute('href').split('/')[-1])
        if user_object:
            user_object['url'] = elem.get_attribute('href')
            user_object['img_url'] = user_img_url
            temp_user_map[i] = user_object
            # user_object['review_title']=review_titles[i-1]
            # user_object['review_content'] = review_contents[i - 1]


            # for i in range(0,10):
            #     try:
            #         elem = browser.find_element_by_class_name('ui_close_x');
            #         browser.find_element_by_class_name('ui_close_x').click()
            #     except:
            #         #browser.find_element_by_css_selector('div .close').click()
            #         if i>8:
            #             browser.find_element_by_class_name('ui_close_x').click()
            #             break
            #         time.sleep(1)

            browser.find_element_by_css_selector('.ui_overlay >  .ui_close_x').click()

    browser.execute_script('scroll(250,0)')
    for moreLink in browser.find_elements_by_css_selector('.entry .taLnk'):
        #if moreLink.value_of_css_property('line-height') == '19px':
            # browser.execute_script('arguments[0].scrollIntoView(true);', moreLink);
            # actions = ActionChains(browser)
            # actions.move_to_element(moreLink).click(moreLink).perform()
        moreLink.click()
        break

    close_popup_if_exists()
    # actions.move_to_element(moreLink).click(moreLink).perform()
    # try:
    #     moreLink.click()
    # except ElementNotVisibleException:
    #     pass

    time.sleep(2)
    review_titles = filter(lambda title: title != '',
                           map(lambda title: title.text, browser.find_elements_by_css_selector('.noQuotes')))
    review_contents = filter(lambda cont: cont != '',
                             map(getReviewContent, browser.find_elements_by_css_selector('.partial_entry')))
    review_ratings = filter(lambda rat: rat != '',
                            map(getRating, browser.find_elements_by_css_selector('.reviewItemInline span')))

    for key in temp_user_map.keys():
        temp_user_map[key]['review_title'] = review_titles[key - 1 + first_page]
        temp_user_map[key]['review_content'] = review_contents[key - 1 + first_page]
        temp_user_map[key]['review_rating'] = review_ratings[key - 1 + first_page ]

    first_page = 1


def move_to_next_page():
    browser.execute_script('scroll(250,0)')
    #browser.find_element_by_partial_link_text("Next").click()
    browser.find_element_by_css_selector(".next").click()
    close_popup_if_exists()
    browser.execute_script('scroll(250,0)')


def scrape_user(user):
    def move_to_next_reviews_page():
        next_btn = browser.find_element_by_id('cs-paginate-next')
        if str(next_btn.get_attribute('class')).find('disabled') > -1:
            return False
        else:
            next_btn.click()
            time.sleep(2)
            return True

    def scrape_badges():
        browser.find_element_by_css_selector('.totalBadges').click()
        wait_by_selector('.badgeText')
        badges = []
        for badge in browser.find_elements_by_css_selector('.badgeText'):
            badges.append(badge.text)
        user['badges'] = badges
        browser.get(user['url'])

    def scrape_reviews(review_type, relevant_map):
        type_btn = browser.find_elements_by_css_selector('[data-filter=' + review_type + ']')
        reviews = {}
        if len(type_btn) > 0:
            type_btn[0].click()
            wait_by_selector('.cs-review-rating')
            time.sleep(1)
            more_pages = True
            while more_pages:
                ratings = map(lambda rating: getRating(rating),
                              browser.find_elements_by_css_selector('.cs-review-rating > span'))

                i = 0
                for review in browser.find_elements_by_css_selector('.cs-review-location > a'):
                    reviews[review.text] = {'rating': ratings[i]}
                    i += 1
                    relevant_map[review.text] = {'url': review.get_attribute('href')}

                more_pages = move_to_next_reviews_page()
        return reviews

    def scrape_cities():
        browser.find_element_by_css_selector('.travelMap').click()
        listView = browser.find_element_by_css_selector('.listView')
        listView.click()

        cities = browser.find_elements_by_css_selector('.cityName')
        last_city = ''
        cur_city = cities[-1].text
        while last_city != cur_city:
            last_city = cities[-1].text
            browser.execute_script('arguments[0].scrollIntoView(true);', cities[-1]);
            time.sleep(1)
            cities = browser.find_elements_by_css_selector('.cityName')
            cur_city = cities[-1].text

        user['cities'] = map(lambda city: city.text, cities)

    browser.get(user['url'])

    user['points'] = browser.find_element_by_css_selector('.points').text

    tags = []
    for tag in browser.find_elements_by_css_selector('.tagBubble'):
        if tag.text != '':
            tags.append(tag.text)
    user['tags'] = tags

    # scrape_badges()

    # user['hotels'] = scrape_reviews('REVIEWS_HOTELS', hotels)
    user['restaurants'] = scrape_reviews('REVIEWS_RESTAURANTS', restaurants)
    # user['attractions'] = scrape_reviews('REVIEWS_ATTRACTIONS', attractions)

    # scrape_cities()


def scrape_restaurant(restaurant):
    print 'scraping ' + restaurant['url']
    html = urllib2.urlopen(restaurant['url']).read()
    parsedHtml = etree.HTML(html)
    details = parsedHtml.cssselect('.table_section > .row')
    for detail in details[1:]:
        title = str.lower(detail.cssselect('.title')[0].text.replace('\n', '').replace(' ', '_'))
        content = detail.cssselect('.content')[0].text.replace('\n', '')
        if content != '':
            restaurant[title] = content

    for locNom in parsedHtml.cssselect('.detail'):
        if locNom.text and locNom.text.find('Location:') > -1:
            locations = locNom.cssselect('span')
            if len(locations) > 0:
                restaurant['continent'] = locations[0].text[1:]
            if len(locations) > 1:
                restaurant['country'] = locations[1].text[5:]
            if len(locations) > 2:
                restaurant['city'] = locations[2].text[5:]


def scrape_poi(url, name):
    init_page(url)
    for i in range(0, 2):
        extract_page_users(name)
        move_to_next_page()


def main():
    with open('pois.json', 'r') as pois_file:
        pois = json.load(pois_file)[:1]

    for poi in pois:
        scrape_poi(poi['url'], poi['name'])

    print json.dumps(users_map)

    for user in users_map.values():
        retry = 3
        while retry > 0:
            try:
                scrape_user(user)
                break
            except Exception:
                retry -= 1

    for restaurant in restaurants.values():
        try:
            scrape_restaurant(restaurant)
        except:
            print 'couldnt parse ' + restaurant['url']
            pass

    with open('users.json', 'w') as users_file:
        json.dump(users_map, users_file)

    with open('rests.json', 'w') as rests_file:
        json.dump(restaurants, rests_file)

    browser.quit()


if __name__ == "__main__":
    main()
