##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################

from bs4 import BeautifulSoup
import re
from collections import OrderedDict
from selenium.common.exceptions import NoSuchElementException

##################################################
##########  GENERAL FUNCTION FOR USE #############
##################################################

def scrape_generalinfo(driver,search_input):
    dict_info = {}
    order = ["search input","google maps name","id","category","address","score","reviews","expense","extrainfo","address",
             "maandag","dinsdag","woensdag","donderdag","vrijdag","zaterdag","zondag"]

    dict_info.update({"search input": search_input})
    dict_info.update({"google maps name": driver.find_elements_by_class_name("section-hero-header-title-title")[0].text})
    dict_info.update({"id": driver.find_element_by_css_selector('span[class*="plus-code"]').find_element_by_xpath('../..').text})
    try:
        image_adr = driver.find_element_by_css_selector('img[src*="place_gm_blue"]').find_element_by_xpath('../..')
        dict_info.update({"address":(list(filter(None,(re.split('   ',BeautifulSoup(image_adr.get_attribute('innerHTML'), 'lxml').text))))[0]).strip()})
    except NoSuchElementException:
        dict_info.update({"address": "no address available"})
    try:
        reviews = driver.find_element_by_css_selector('button[jsaction="pane.rating.moreReviews"]').text
        dict_info.update({"reviews":re.findall(r'\d+',reviews)[0]})
    except NoSuchElementException:
        dict_info.update({"reviews": "no reviews available"})
    try:
        dict_info.update({"score": driver.find_element_by_css_selector('span[class="section-star-display"]').text})
    except NoSuchElementException:
        dict_info.update({"score": "no reviews available"})
    try:
        dict_info.update({"expense":driver.find_element_by_css_selector('span[aria-label*="Prijs"]').text})
    except NoSuchElementException:
        dict_info.update({"expense": "no expense available"})
    try:
        dict_info.update({"category": driver.find_element_by_css_selector('button[jsaction="pane.rating.category"]').text})
    except NoSuchElementException:
        dict_info.update({"category": "no category available"})
    try:
        dict_info.update({"extrainfo":driver.find_element_by_css_selector('div[class*="editorial-attributes-summary"]').text})
    except NoSuchElementException:
        dict_info.update({"extrainfo": "no extra info available"})

    try:
        openinghours = driver.find_element_by_css_selector('div[class*="section-open-hours"]').get_attribute("aria-label")
        openinghours = openinghours.split(",")
        for day in openinghours:
            day_split = day.split(" ",1)
            dict_info.update({day_split[0]:day_split[1]})
    except NoSuchElementException:
        dict_info.update({"maandag": "no hours available","dinsdag":"no hours available","woensdag": "no hours available",
                          "donderdag":"no hours available","vrijdag":"no hours available",
                          "zaterdag":"no hours available","zondag":"no hours available"})
    finally:
        ordered_general_info = OrderedDict((k, dict_info[k]) for k in order)

    return ordered_general_info
