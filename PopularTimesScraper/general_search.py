##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################

import re
import pandas as pd
import time
from collections import defaultdict
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


##############################################
##########  IMPORT OWN FUNCTIONS LIBRARIES ###
##############################################

from PopularTimesScraper.formatting_data import appending_data
from PopularTimesScraper.formatting_data import dataframe_poptimes
from PopularTimesScraper.pop_times import scrape_pop
from PopularTimesScraper.scrape_info import scrape_generalinfo

##############################################
##########  SUPPORTIVE FUNCTIONS #############
##############################################

def scrapepage(driver,search_input,general_popdata,general_popdatacol,general_datacol,general_data):
    for i in range(1):
        global result
        time.sleep(1)
        print(i)
        try:
            result = driver.find_elements_by_css_selector('h3[class="section-result-title"]')[i]
        except:
            break
        ActionChains(driver).move_to_element(result).perform()  # scroll to element
        result.click()
        try:
            driver.find_element_by_css_selector('div[class="section-hero-header-title-description"]')
        except NoSuchElementException:
            driver.find_element_by_xpath("//span[contains(@class,'button-previous-icon')]").click()
            time.sleep(4)
            driver.find_element_by_xpath("//span[contains(@class,'button-next-icon')]").click()
            time.sleep(4)
        populartimesgraph = scrape_pop(driver,search_input)
        appendedpoptimes = appending_data(populartimesgraph, general_popdatacol,general_popdata)
        generalinfo = scrape_generalinfo(driver,search_input)
        appendedgeneralinfo = appending_data(generalinfo,general_datacol,general_data)
        titlepage = driver.find_element_by_css_selector(('div[class="section-hero-header-title-description"]')).text
        print(titlepage)
        backbutton = driver.find_elements_by_xpath("//button[contains(@class,'back-to-list')]")
        backbutton[0].click()
        time.sleep(4)
    return [appendedpoptimes,appendedgeneralinfo]

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
    general_popdatacol  = defaultdict(list)
    general_popdata  = {}
    general_datacol  = defaultdict(list)
    general_data  = {}
    global page_available,lat_diff,long_diff
    page_available = 1
    original_geocode = get_geo(driver)
    while page_available == 1:
        current_geocode = get_geo(driver)
        lat_diff = abs(current_geocode[0] - original_geocode[0])
        long_diff = abs(current_geocode[1] - original_geocode[1])
        if lat_diff < 0.2 and long_diff < 0.2:
            scraperesults = scrapepage(driver,search_input,general_popdata,general_popdatacol,general_datacol,general_data)
            try:
                pagenext = driver.find_elements_by_xpath("//span[contains(@class,'button-next-icon')]")
                page_available = 1
                pagenext[0].click()
                time.sleep(5)
            except:
                page_available = 0
                break
        else:
            page_available = 0
            break
    poptimes_data_final = dataframe_poptimes(scraperesults[0])
    generalinfo_data_final = pd.DataFrame.from_dict(scraperesults[1])
    return [poptimes_data_final, generalinfo_data_final]

#################################################