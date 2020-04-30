##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################

from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import OrderedDict
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from collections import defaultdict



##################################################
##########  GENERAL FUNCTION FOR USE #############
##################################################

def scrape_generalinfo(driver,search_input):
    search_input_list = search_input
    google_maps_name = driver.find_elements_by_class_name("section-hero-header-title-title")[0].text
    url = driver.current_url
    try:
        id_coordinates = driver.find_element_by_css_selector('span[class*="plus-code"]')
        ActionChains(driver).move_to_element(id_coordinates).perform()
        id_list = id_coordinates.find_element_by_xpath('../..').text
    except NoSuchElementException:
        id_list = "no id available"
    try:
        image_adr = driver.find_element_by_css_selector('img[src*="place_gm_blue"]').find_element_by_xpath('../..')
        address = list(filter(None,(re.split('   ',BeautifulSoup(image_adr.get_attribute('innerHTML'), 'lxml').text))))[0].strip()
    except NoSuchElementException:
        address = "no address available"
    try:
        reviews_raw = driver.find_element_by_css_selector('button[jsaction="pane.rating.moreReviews"]').text
        reviews = re.findall(r'\d+',reviews_raw)[0]
    except NoSuchElementException:
        reviews = "no reviews available"
    try:
        score = driver.find_element_by_css_selector('span[class="section-star-display"]').text
    except NoSuchElementException:
        score ="no reviews available"
    try:
        expense = driver.find_element_by_css_selector('span[aria-label*="Prijs"]').text
    except NoSuchElementException:
        expense = "no expense available"
    try:
        category = driver.find_element_by_css_selector('button[jsaction="pane.rating.category"]').text
    except NoSuchElementException:
        category = "no category available"
    try:
        extrainfo = driver.find_element_by_css_selector('div[class*="editorial-attributes-summary"]').text
    except NoSuchElementException:
        extrainfo = "no extra info available"

    dict_days = defaultdict(list)
    try:
        openinghours = driver.find_element_by_css_selector('div[class*="section-open-hours"]').get_attribute("aria-label")
    except NoSuchElementException:
        dict_days['maandag'] = dict_days['dinsdag'] = dict_days['woensdag'] = \
            dict_days['donderdag'] = dict_days['vrijdag'] = dict_days['zaterdag'] = dict_days['zondag'] = ['no hours available']
    else:
        openinghours = openinghours.split(",")
        for day in openinghours:
            day_split = day.split(" ",1)
            dayname = day_split[0]
            dict_days[dayname] = day_split[1]
    finally:
        dict_generalinfo = {'url':url,'search input':search_input_list,'google maps name':google_maps_name,'id':id_list,'category':category,
                         'address':address,'score':score,'reviews':reviews,'expense':expense,'extra info':extrainfo,'maandag':dict_days['maandag'],
                            'dinsdag':dict_days['dinsdag'],'woensdag':dict_days['woensdag'],'donderdag':dict_days['donderdag'],'vrijdag':dict_days['vrijdag'],
                            'zaterdag':dict_days['zaterdag'],'zondag':dict_days['zondag']}
    return dict_generalinfo