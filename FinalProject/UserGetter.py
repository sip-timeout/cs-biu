from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
import  re


browser = webdriver.Chrome()
browser.maximize_window()
browser.get('https://www.tripadvisor.com/Restaurant_Review-g293984-d2410151-Reviews-Hatraklin_Bistro_Meat_Wine-Tel_Aviv_Tel_Aviv_District.html')

elem = browser.find_element_by_tag_name('a')
elem.click()

WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CLASS_NAME,'member_info')))

users = []
userMap = {}

def extractUserPreview(userName):
    user = {}

    if len(browser.find_elements_by_css_selector(".reviewchart")) == 0:
        return False


    user ["userName"] =userName
    user["name"] = browser.find_element_by_css_selector("h3.username").text

    try:
        user["level"] = browser.find_element_by_css_selector(".badgeinfo span").text
    except NoSuchElementException:
        pass

    for desc in browser.find_elements_by_css_selector(".memberdescription li"):
        descTXT = str(desc.text).lower()
        if descTXT.find('since') > -1:
            user["joinDate"] = descTXT.split(' ')[-1]
        if descTXT.find('from') > -1:
            user["location"] = descTXT[descTXT.find('from') + 5:]
        if descTXT.find('man ') > -1:
            user["gender"] = "M"
        if descTXT.find('woman ') > -1:
            user["gender"] = "F"
        if re.match('[0-9]{2}-[0-9]{2}',descTXT):
            st,end = re.match('[0-9]{2}-[0-9]{2}', descTXT).regs[0]
            user["age"] = descTXT[st:end+1]

    revDist = []
    for revCount in browser.find_elements_by_css_selector(".barchartmemoverlay .row .numbersText"):
        revDist.append(str(revCount.text).strip('(').strip(')'))

    user["reviewDist"] = revDist


    def getCountValue(countHTML):
        startidx = countHTML.find('>')+1
        endidx = countHTML.find('<',startidx)
        return countHTML[startidx:endidx]

    for count in browser.find_elements_by_css_selector(".counts li"):
        countHtml = str(count.get_attribute("innerHTML"))
        if countHtml.find("Contributions") > -1:
            user["contrib"] = getCountValue(countHtml)
        if countHtml.find("Helpful") > -1:
            user["helpful"] = getCountValue(countHtml)
        if countHtml.find("Cities") > -1:
            user["cities"] = getCountValue(countHtml)

    userMap[userName] = user
    return True


def extactPageUsers():
    elems = browser.find_elements_by_class_name('member_info')
    for i in range(1, 11):

        elem = elems[i]
        try:
            elem.click()
        except StaleElementReferenceException:
            continue

        time.sleep(0.5)
        try:
            elem = browser.find_element_by_partial_link_text("profile")
        except NoSuchElementException:
            browser.find_element_by_class_name('ui_close_x').click()
            continue

        if extractUserPreview(elem.get_attribute('href').split('/')[-1]):
            users.append(elem.get_attribute('href'))
        browser.find_element_by_class_name('ui_close_x').click()


extactPageUsers()
browser.find_element_by_partial_link_text("Next").click()
time.sleep(1)
browser.find_element_by_class_name('ui_close_x').click()
browser.find_element_by_partial_link_text("Next").click()

#extactPageUsers()


for user in userMap.values():
    print user


print 'Page Ready!'

browser.quit()

