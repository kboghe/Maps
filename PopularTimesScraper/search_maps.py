##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################

from selenium.webdriver.common.keys import Keys
import time

##########################################
##########  SUPPORTIVE FUNCTIONS #########
##########################################

def literal_search(driver):
    # force the search to be literal (to avoid ambiguous station names) if Google corrects your search term
    check_correction_link = driver.find_elements_by_css_selector('button[jsaction="pane.correctionSection.originalQueryClick"]')  # find a link referring to your original search term.
    if len(check_correction_link) > 0:  # if you can find that link (i.e. length of element is longere than 0)...
        check_correction_link[0].click()  # ...click on it

##################################################
##########  GENERAL FUNCTION FOR USE #############
##################################################

def start_session(driver):
    driver.get("https://www.google.be/maps") #start up the browser and go to Google Maps
    driver.implicitly_wait(6)
    driver.find_element_by_xpath("//button[contains(text(),'Mij later herinneren')]").click() #click on privacy reminder if it pops up (it may hinder us from scraping some elements hidden behind the pop-up)
    return driver

def search_maps(driver,search_term):
    search_bar = driver.find_element_by_name("q") #find the search bar
    search_bar.clear() #clear it (i.e. delete whatever's typed into it)
    search_bar.send_keys(search_term) #typ in the search term (we've just defined) into the search bar...
    search_bar.send_keys(Keys.RETURN)  #...and press enter
    literal_search(driver)
    time.sleep(3)
    return driver