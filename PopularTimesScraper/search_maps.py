##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import time

##########################################
##########  SUPPORTIVE FUNCTIONS #########
##########################################

###############################################
def literal_search(driver):
    # force the search to be literal (to avoid ambiguous station names) if Google corrects your search term
    check_correction_link = driver.find_elements_by_css_selector('button[jsaction="pane.correctionSection.originalQueryClick"]')  # find a link referring to your original search term.
    try:  # if you can find that link (i.e. length of element is longere than 0)...
        check_correction_link[0].click()  # ...click on it
    except:
        pass

#################################################
def distance_check(driver):
    scale = driver.find_element_by_css_selector('button[class*= "widget-scale"]')
    scale_text = BeautifulSoup(scale.get_attribute('innerHTML'), 'lxml')  #load it into Beautifulsoup
    dist = scale_text.select('label#widget-scale-label')[0].text.split(' ')
    if dist[1] == "km":
        dist[1] = "000"
    else:
        dist[1] = ""
    dist = int(dist[0] + dist[1])
    only_num = re.compile(r'[^\d]')
    length_bar = int(only_num.sub('',scale_text.div["style"]))
    return [dist,length_bar]

###################################################
def zoom_check(dist_original,dist_new):
    zoom = "ok"
    if dist_original[0] < dist_new[0]:
        zoom = "zooming out"
    if (dist_original[0] == dist_new[0]) and (dist_original[1] > dist_new[1]):
        zoom = "zooming out"
    return [zoom]

##################################################
##########  GENERAL FUNCTION FOR USE #############
##################################################

def start_session(driver):
    driver.get("https://www.google.be/maps") #start up the browser and go to Google Maps
    driver.implicitly_wait(6)
    driver.find_element_by_xpath("//button[contains(text(),'Mij later herinneren')]").click() #click on privacy reminder if it pops up (it may hinder us from scraping some elements hidden behind the pop-up)
    return driver

def search_maps(driver,search_term):
    while True:
        search_bar = driver.find_element_by_name("q") #find the search bar
        search_bar.clear() #clear it (i.e. delete whatever's typed into it)
        for letter in search_term: #create a delay in sending the keys to avoid
            time.sleep(0.5)
            search_bar.send_keys(letter)
        search_bar.send_keys(Keys.RETURN)  #...and press enter
        input_new = driver.find_element_by_tag_name('title').get_attribute('innerHTML').split('-')[0].strip()
        if input_new == search_term:
            time.sleep(5)
            literal_search(driver)
            break
        else:
            time.sleep(3)
            pass
    return driver

def nearby_or_freewheeling(driver,search_input,search_term):
        #try out the nearby option and see how that changes the range in maps#
        dist_original = distance_check(driver)
        time.sleep(2)
        nearby = driver.find_element_by_css_selector('button[jsaction="pane.placeActions.nearby"]')
        driver.execute_script("arguments[0].click();",nearby)
        driver = search_maps(driver, search_term)
        dist_new = distance_check(driver)
        zoom = zoom_check(dist_original,dist_new)[0]

        #use the nearby function only if Google doesn't zoom out even further from your place of interest.
        # Otherwise, perform the search again#
        if zoom == "ok":
            try:
                nopreview = driver.find_element_by_css_selector('input[aria-checked="true"]')
                driver.execute_script("arguments[0].click();",nopreview)
            except NoSuchElementException:
                pass

        if zoom == "zooming out":
            driver = search_maps(driver, search_input)
            driver = search_maps(driver, search_term)

        return driver
