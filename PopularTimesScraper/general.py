##############################################
##########  IMPORT GENERAL LIBRARIES #########
##############################################
from selenium import webdriver
import pandas as pd
import time
import os

##############################################
##########  IMPORT OWN FUNCTIONS LIBRARIES ###
##############################################
from PopularTimesScraper.indirect_search import ind_search, no_place_found
from PopularTimesScraper.general_search import general_search
from PopularTimesScraper.specific_place import scrape_specific_page
from PopularTimesScraper.search_maps import start_session, search_maps, nearby_or_freewheeling
from PopularTimesScraper.ConnectionMySQL import mysql_start, create_table_generalinfo_db, create_table_popinfo_db, upload_to_db
from PopularTimesScraper.VPNConnect import StatuscheckVPN, VPNrotate

###########################
####  define parameters ###
###########################
search_type = "general"
literal_search = "true"
category_search = "false"
pop_scraping = "true"
general_scraping = "true"

###################################
####  initiate MYSQL connection ###
###################################

mysql_initiate =mysql_start(host='localhost',database="googlemaps_scraper",user="kboghe",password="GhostInTheShell20!")
connection = mysql_initiate[0]
cursor = mysql_initiate[1]

mysql_table_pop = "populartimes_places"
mysql_table_geninfo = "generalinfo_places"

#create_table_generalinfo_db(cursor,mysql_table_geninfo)
#create_table_popinfo_db(cursor,mysql_table_pop)

#################################
##### initiate VPN connection####
#################################
geo = StatuscheckVPN()

###########################
####  load search input ###
###########################
inputfile_search = pd.read_csv('./inputfile_search.csv', sep=";", encoding='utf-8')
inputfile_search = inputfile_search.iloc[10:]

#########################
####scrape Google maps###
#########################
for index, row in inputfile_search.iterrows():
    search_term = row[1]
    search_input = row[0]

    #  start browser#
    driver = webdriver.Chrome('./chromedriver')  # define location of the ChromeDriver (just put it in the same folder as the script)#
    driver = start_session(driver)

    # define search input#
    driver = search_maps(driver, search_input)

    if search_type == "general":
        driver = nearby_or_freewheeling(driver,search_input,search_term)
    else:
        time.sleep(3)
        driver = search_maps(driver, search_term)

    # check whether Maps immediately found a specific page#
    individual_location_page = len(driver.find_elements_by_class_name("section-hero-header-title-description"))  # check whether Maps already found a specific page by looking for a Google place title

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
            output = general_search(driver,search_input)
        if check_number_results == 0:
            output = no_place_found(search_input)

    #####################
    #write to hard drive#
    #####################
    populartimes_file = os.getcwd() + "/scraped_results/" + search_input + "_" + "poptimes" + "_"+ search_term + ".csv"
    generalinfo_file = os.getcwd() + "/scraped_results/" + search_input + "_" + "generalinfo" + "_"+ search_term + ".csv"
    output[0].to_csv(populartimes_file)
    output[1].to_csv(generalinfo_file)

    ##################################
    #add the info to a MYSQL database#
    ##################################
    upload_to_db(cursor, generalinfo_file,mysql_table_geninfo)
    upload_to_db(cursor,populartimes_file,mysql_table_pop)

    ##############
    #close driver#
    ##############
    driver.close()

    ##############################
    #rotate servers using NordVPN#
    ##############################
    VPNrotate(geo)