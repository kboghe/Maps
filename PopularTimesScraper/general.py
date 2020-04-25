########
#IMPORT#
########

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
from collections import defaultdict
import re
from collections import OrderedDict


from PopularTimesScraper.pop_times import scrape_pop
from PopularTimesScraper.indirect_search import ind_search
from PopularTimesScraper.formatting_data import appending_poptimes, dataframe_poptimes
from PopularTimesScraper.general_search import general_search
from PopularTimesScraper.scrape_info import scrape_generalinfo

#############################
##### load search input #####
#############################

search_inputs = pd.read_csv("/home/cc/PycharmProjects/DigitalMethodsExercises/Infrabel challenge/input_pop_times.csv", sep=",") #import csv file containing a list of places you want to search for
search_inputs = search_inputs.iloc[:,0] #extract the column containing the list of search terms

###################################################
###### prepare general dataset to store all info###
###################################################

stations_all = pd.DataFrame(columns=["station","title_google","category_google","day_of_week","percentage busy","hour","hours_in_day"]) #we'll append the variables we'll scrape from a single search to this general dataset, containing all our results in the end

##################################
##### start the chromedriver #####
##################################

driver = webdriver.Chrome('./chromedriver') #define location of the ChromeDriver (just put it in the same folder as the script)
driver.get("https://www.google.be/maps") #start up the browser and go to Google Maps
driver.implicitly_wait(10) #let the driver wait for a maximum of 10 seconds to fetch certain elements (if it needs to load a page and some elmements are not yet available). The driver will try to access the element for 10 seconds and will continue scraping automatically if it finds the element in less than 10 seconds. This setting will be applied for the entire driver session.
driver.find_element_by_xpath("//button[contains(text(),'Mij later herinneren')]").click() #click on privacy reminder if it pops up (it may hinder us from scraping some elements hidden behind the pop-up)

##################################
##### loop all search inputs #####
##################################

for element in search_inputs: #for every search term you've exctracted from your general dataset...
    search_input = element
    print('\033[1m' + "***LOOKING FOR A TRAIN STATION IN " + search_input + ".***")
    print('\033[0m')

    #prepare some empty lists to store information
    #day_list,percentage_list,hour_list,station,name_google,category_google,hours_in_day = ([] for i in range(7))

    #######################
    ##define search input##
    #######################

    search_bar = driver.find_element_by_name("q") #find the search bar
    search_bar.clear() #clear it (i.e. delete whatever's typed into it)
    search_term = search_input + " " + "train" #define the specific search term we'd like to search for (e.g. a particular city + "train")

    #dealing with some tough exceptions. Change the search term if it is one of these exceptions
    if search_term == "ANTWERPEN-CAAL train":
        search_term = "69,, Pelikaanstraat 59"
    if search_term == "BRU.-MIDI/ZUID train":
        search_term = "BRUSSEL-ZUID train"
    if search_term == "BRU.-CONG. train":
        search_term = "BRUSSEL-CONGRES train"
    if search_term == "BRU.-WEST/OUEST train":
        search_term = "BRUSSEL-WEST train"

    search_bar.send_keys(search_term) #typ in the search term (we'ce just defined) into the search bar...
    search_bar.send_keys(Keys.RETURN)  #...and press enter
    time.sleep(5) #let the script sleep for 5 seconds

    ########################
    ##force literal search##
    ########################

    #force the search to be literal (to avoid ambiguous station names) if Google corrects your search term
    check_correction_link = driver.find_elements_by_css_selector('button[jsaction="pane.correctionSection.originalQueryClick"]') #find a link referring to your original search term.
    if len(check_correction_link) > 0: #if you can find that link (i.e. length of element is longere than 0)...
        check_correction_link[0].click() #...click on it

    #check whether Google maps found a particular page immediately#
    check_individual_page = driver.find_elements_by_class_name("section-hero-header-title-description") #check whether Maps already found a specific page by looking for a Google place title
    individual_location_page = len(check_individual_page) #save the length of this element

    #perform indirect search if necessary#
    if individual_location_page == 0:  # if the driver did not found a specific page...
        individual_location_page = ind_search(driver,search_input)
        time.sleep(8)

    #scrape popular times graph#
    populartimesgraph = scrape_pop(driver,search_input)
    general_popdatacol = appending_poptimes(populartimesgraph)

dataframe_poptimes(general_popdatacol)


    ##################
    #create dataframe#
    ##################

    dict_station = {"station": station, "title_google": name_google, "category_google": category_google, "day_of_week":day_list,"percentage busy": percentage_list,"hour":hour_list, "hours_in_day": hours_in_day} #create dictionary to construct a DataFrame
    station_specific = pd.DataFrame(dict_station) #use this dictionary to construct dataframe. This DataFrame contains all info of one particular station
    stations_all = pd.concat([stations_all,station_specific]) #add the info of this particular station to a general dataframe containing info on all stations( that we've scraped up until now)
    print("Going to next station...\n")

driver.close() #if the driver went through each and every search term, close the driver (this will close the browser session)

stations_all.to_csv("", sep=";", header=True) #write this DataFrame to your hard drive

################
#ERROR CHECKING#
################

stations_final_results = stations_all #create a copy of your final results

stations_final_results.iloc[:,1] = (stations_final_results.iloc[:,1]).str.lower() #set the Google placename to lowercase (e.g. AALST station --> aalst)
stations_final_results.iloc[:,0] = (stations_final_results.iloc[:,0]).str.lower()  #set the search term to lowercase (e.g. AALST --> aalst)

names_stations_match = stations_final_results.iloc[:,[0,1]] #extract these two columns from the DataFrame
names_stations_match = names_stations_match.drop_duplicates() #drop all the duplicates (so you only keep one search term --> Google place name match)
names_stations_match = names_stations_match[names_stations_match.iloc[:,1] != "no popular times available!"] #drop stations where no popular times were available
names_stations_match['match'] = np.where(names_stations_match.iloc[:,0] == names_stations_match.iloc[:,1], "perfect match", "non-perfect match") #create a new column 'match'. If the search term matches the Google place name, give it the value 'perfect match', otherwise give it the value 'non-perfect match'
stations_to_check = names_stations_match[names_stations_match['match'] == "non-perfect match"] #extract the non-perfect matches

########################################################################################################################################

testje = general_search(driver,search_input)


#######################################################################################################################################


