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

######################################
def retry_page(driver,count):
    previous = driver.find_element_by_xpath("//span[contains(@class,'button-previous-icon')]")
    driver.execute_script("arguments[0].click();", previous)
    time.sleep(8)
    next = driver.find_element_by_xpath("//span[contains(@class,'button-next-icon')]")
    driver.execute_script("arguments[0].click();", next)
    time.sleep(8)
    result = driver.find_elements_by_css_selector('h3[class="section-result-title"]')[count]
    ActionChains(driver).move_to_element(result).perform()
    driver.execute_script("arguments[0].click();", result)

######################################
def get_geo(driver):
    url = driver.current_url
    geocode = re.search(r'(?<=@)(.*?),(.*?)(?=,)', url)[0]
    latitude = float(geocode.split(',')[0])
    longitude = float(geocode.split(',')[1])
    return latitude, longitude

########################################

def no_appropriate_places(search_input):
        place_not_found = "page without results"  # and append this message to every list (we'll use these lists to create our general DataFrame later on)
        name_google = hours_in_day = percentage_list = hour_list = day_list = id = place_not_found
        dict_poptimes = {'search input': search_input, 'google maps name': name_google, 'id': id,'hours in day': hours_in_day, 'percentage busy': percentage_list, 'hour list': hour_list,'day list': day_list}
        dict_generalinfo = {'search input': search_input, 'google maps name': place_not_found, 'id': place_not_found,'category': place_not_found,'address': place_not_found, 'score': place_not_found, 'reviews': place_not_found,'expense': place_not_found,'extra info': place_not_found, 'maandag': place_not_found, 'dinsdag': place_not_found,'woensdag': place_not_found,'donderdag': place_not_found, 'vrijdag': place_not_found, 'zaterdag': place_not_found,'zondag': place_not_found}
        return [dict_poptimes, dict_generalinfo]

###############################################

def scrapepage(driver,search_input,general_popdata,general_popdatacol,general_datacol,general_data,original_geocode):
    for i in range(20):
        global result, count, populartimesgraph, generalinfo, appendedpoptimes, appendedgeneralinfo
        count = i
        places_toofar = 0
        time.sleep(5)
        no_places_on_page = len(driver.find_elements_by_css_selector('div[class=".section-no-result.noprint"]'))
        if no_places_on_page == 1:
            break
        if no_places_on_page == 0:
            try:
                result = driver.find_elements_by_css_selector('h3[class="section-result-title"]')[i]
            except IndexError:
                break
            else:
                ActionChains(driver).move_to_element(result).perform()  # scroll to element
                driver.execute_script("arguments[0].click();", result)
            try:
                driver.find_element_by_css_selector('div[class="section-hero-header-title-description"]')
            except NoSuchElementException:
                retry_page(driver,count)
            finally:
                time.sleep(4)
                place_geo = get_geo(driver)
                lat_diff_place = abs(place_geo[0] - original_geocode[0])
                long_diff_place = abs(place_geo[1] - original_geocode[1])

            if lat_diff_place > 0.2 or long_diff_place > 0.2:
                print("Searched too far from point of interest. Returning...")
                backbutton = driver.find_element_by_xpath("//button[contains(@class,'back-to-list')]")
                driver.execute_script("arguments[0].click();", backbutton)
                places_toofar = places_toofar + 1

                if places_toofar == 20:
                    empty_dicts = no_appropriate_places(search_input)
                    populartimesgraph = empty_dicts[0]
                    generalinfo = empty_dicts[1]

                continue

            populartimesgraph = scrape_pop(driver, search_input)
            generalinfo = scrape_generalinfo(driver, search_input)
            print("Scraped the following place:")
            print(generalinfo['google maps name'])
            print("#######################")

        appendedpoptimes = appending_data(populartimesgraph, general_popdatacol,general_popdata)
        appendedgeneralinfo = appending_data(generalinfo,general_datacol,general_data)
        backbutton = driver.find_element_by_xpath("//button[contains(@class,'back-to-list')]")
        driver.execute_script("arguments[0].click();",backbutton)
        time.sleep(6)

    return [appendedpoptimes,appendedgeneralinfo]

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
            scraperesults = scrapepage(driver,search_input,general_popdata,general_popdatacol,general_datacol,general_data,original_geocode)
            try:
                pagenext = driver.find_element_by_xpath("//span[contains(@class,'button-next-icon')]")
                page_available = 1
                driver.execute_script("arguments[0].click();",pagenext)
                time.sleep(6)
                error_loading_page = len(driver.find_elements_by_css_selector(".div.section-refresh-overlay.noprint.section-refresh-overlay-visible"))
                if error_loading_page > 0:
                    print("Sorry, Google refuses to load the next page...\nSaving the info I can and moving on.")
                    page_available = 0
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