##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################

import re
import time
from collections import defaultdict
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

##############################################
##########  IMPORT OWN FUNCTIONS LIBRARIES ###
##############################################

from PopularTimesScraper.formatting_data import appending_poptimes
from PopularTimesScraper.formatting_data import dataframe_poptimes
from PopularTimesScraper.pop_times import scrape_pop
from PopularTimesScraper.scrape_info import scrape_generalinfo

##############################################
##########  SUPPORTIVE FUNCTIONS #############
##############################################

def scrapepage(driver,search_input,general_popdata,general_popdatacol):
    for i in range(2):
        time.sleep(1)
        print(i)
        try:
            result = driver.find_elements_by_css_selector('h3[class="section-result-title"]')[i]
        except:
            break
        ActionChains(driver).move_to_element(result).perform()  # scroll to element
        result.click()
        populartimesgraph = scrape_pop(driver,search_input)
        generalinfo = scrape_generalinfo(driver,search_input)
        appendedpoptimes = appending_poptimes(populartimesgraph, general_popdatacol, general_popdata)
        titlepage = driver.find_elements_by_css_selector(('div[class="section-hero-header-title-description"]'))
        title = BeautifulSoup(titlepage[0].get_attribute('innerHTML'), 'lxml').text
        print(title)
        backbutton = driver.find_elements_by_xpath("//button[contains(@class,'back-to-list')]")
        backbutton[0].click()
        time.sleep(10)
    return appendedpoptimes

######################################

def get_geo(driver):
    url = driver.current_url
    geocode = re.search(r'(?<=@)(.*?),(.*?)(?=,)', url)[0]
    latitude = float(geocode.split(',')[0])
    longitude = float(geocode.split(',')[1])
    return latitude, longitude

##################################################
##########  GENERAL FUNCTION FOR USE #############
##################################################

def general_search(driver,search_input):
    general_popdatacol = defaultdict(list)
    general_popdata = {}
    global page_available
    page_available = 1
    original_geocode = get_geo(driver)
    while page_available == 1:
        current_geocode = get_geo(driver)
        lat_diff = current_geocode[0] - original_geocode[0]
        long_diff = current_geocode[1] - original_geocode[1]
        if (lat_diff < 0.2) and (long_diff < 0.2):
            appendedpoptimes = scrapepage(driver,search_input,general_popdata,general_popdatacol)
            try:
                pagenext  = driver.find_elements_by_xpath("//span[contains(@class,'button-next-icon')]")
                page_available = 1
                pagenext[0].click()
            except:
                page_available = 0
                break
        else:
            page_available = 0
            break
    poptimes_data_final = dataframe_poptimes(appendedpoptimes)
    return poptimes_data_final

#################################################