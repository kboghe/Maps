##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################
from selenium import webdriver
import pandas as pd
import time

##############################################
##########  IMPORT OWN FUNCTIONS LIBRARIES ###
##############################################
from PopularTimesScraper.indirect_search import ind_search, no_place_found
from PopularTimesScraper.general_search import general_search
from PopularTimesScraper.specific_place import scrape_specific_page
from PopularTimesScraper.search_maps import start_session, search_maps

###########################
####  define parameters ###
###########################
search_type = "general"
literal_search = "true"
category_search = "false"
pop_scraping = "true"
general_scraping = "true"

###########################
####  load search input ###
###########################
inputfile_search = pd.read_csv('inputfile_search.csv', sep = ";", encoding = 'utf-8')

######################
####  start browser###
######################
driver = webdriver.Chrome('./chromedriver')  # define location of the ChromeDriver (just put it in the same folder as the script)#
driver = start_session(driver)

###########################
####  scrape Google maps###
###########################
for index, row in inputfile_search.iterrows():
    search_term = row[1]
    search_input = row[0]

    ##### load search input #####
    # search_inputs = pd.read_csv("/home/cc/PycharmProjects/DigitalMethodsExercises/Infrabel challenge/input_pop_times.csv", sep=",") #import csv file containing a list of places you want to search for
    # search_inputs = search_inputs.iloc[:,0] #extract the column containing the list of search terms

    #define search input#
    driver = search_maps(driver, search_input)
    driver = search_maps(driver, search_term)

    # check whether Maps immediately found a specific page#
    individual_location_page = len(driver.find_elements_by_class_name(
        "section-hero-header-title-description"))  # check whether Maps already found a specific page by looking for a Google place title

    # if yes, scrape specific page#
    if individual_location_page == 1:
            output = scrape_specific_page(driver, search_input)

    # if not.....#
    # ...1. and the user want to perform a specific search....#
    if individual_location_page == 0 and search_type == "specific":
        individual_location_page = ind_search(driver, search_input)
        time.sleep(8)
        if individual_location_page == 0:
            output = no_place_found(search_input)
        if individual_location_page == 1:
            output = scrape_specific_page(driver, search_input)

    # ...2. and the user want to perform a general search....#
    if individual_location_page == 0 and search_type == "general":
        check_number_results = len(driver.find_elements_by_class_name("section-result-title"))
        if check_number_results > 0:
            output = general_search(driver, search_input)
        if check_number_results == 0:
            output = no_place_found(search_input)

    populartimes_file = search_input + "_" + "poptimes" + "_"+ search_term + ".csv"
    generalinfo_file = search_input + "_" + "generalinfo" + "_"+ search_term + ".csv"
    output[0].to_csv(populartimes_file)
    output[1].to_csv(generalinfo_file)