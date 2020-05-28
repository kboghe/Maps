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
import time

##################################################
########### SUPPORTIVE FUNCTIONS #################
##################################################
def clean_text(text):
    rgx_list = [r'\(.*?\)',r'Openingstijden.*']
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, '', new_text).strip()
    return new_text

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
        extracontainer = driver.find_element_by_css_selector('div[class*="section-editorial-attributes-summary"]')
    except NoSuchElementException:
        extrainfo = "no extra info available"
    else:
        driver.execute_script("arguments[0].click();", extracontainer)
        time.sleep(4)

        extrainfotables = driver.find_elements_by_css_selector('div[class="section-attribute-group GLOBAL__gm2-body-2"]')
        extrainfo = list()
        for table in extrainfotables:
            table_soup = BeautifulSoup(table.get_attribute('innerHTML'),'lxml')
            title_info = table_soup.select('div[class*="group-title"]')[0].text.strip()
            title_content = table_soup.select('div[class*="group-item"]')

            contentlist = list()
            for i in range(len(title_content)):
                content = title_content[i].text.strip()
                contentlist.append(content)
            contentlist = '#'.join(contentlist).replace("##","#")

            info_single_table = title_info + " *** " + contentlist
            print(info_single_table)
            extrainfo.append(info_single_table)
            print("##########")
        extrainfo = ' --- '.join(extrainfo)

        time.sleep(2)
        backbutton = driver.find_element_by_css_selector('button[class*="section-header-back-button"]')
        driver.execute_script("arguments[0].click();", backbutton)
        time.sleep(4)

    dict_days = defaultdict(list)
    message_empty = "no hours available"
    dict_days_empty = {'maandag': message_empty, 'dinsdag': message_empty, 'woensdag': message_empty, 'donderdag':message_empty,
                       'vrijdag': message_empty, 'zaterdag': message_empty, 'zondag': message_empty}
    try:
        openinghours = driver.find_element_by_css_selector('div[class*="section-open-hours"]').get_attribute("aria-label")
    except NoSuchElementException:
        dict_days = dict_days_empty
    else:
        if str(next(iter(dict_days_empty))) in openinghours:
            count_semicolon = openinghours.count(";")
            if count_semicolon == 0:
                openinghours = openinghours.split(",")
            elif count_semicolon > 0:
                openinghours = openinghours.split(";")

            for day in openinghours:
                count_comma = openinghours[0].count(",")
                if count_comma > 0:
                    day_split = day.split(",",1)
                else:
                    day_split = day.split(" ", 1)
                dayname = day_split[0].strip()
                dict_days[dayname] = clean_text(day_split[1])
        else:
            dict_days = dict_days_empty

    dict_generalinfo = {'url':url,'search input':search_input_list,'google maps name':google_maps_name,'id':id_list,'category':category,
                        'address':address,'score':score,'reviews':reviews,'expense':expense,'extra info':extrainfo,'maandag':dict_days['maandag'],
                        'dinsdag':dict_days['dinsdag'],'woensdag':dict_days['woensdag'],'donderdag':dict_days['donderdag'],'vrijdag':dict_days['vrijdag'],
                        'zaterdag':dict_days['zaterdag'],'zondag':dict_days['zondag']}
    return dict_generalinfo