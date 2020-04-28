##############################################
##########  IMPORT OWN FUNCTIONS LIBRARIES ###
##############################################

from PopularTimesScraper.pop_times import scrape_pop
from PopularTimesScraper.general_search import scrape_generalinfo

##################################################
##########  GENERAL FUNCTION FOR USE #############
##################################################

def scrape_specific_page(driver,search_input):
    populartimesgraph = scrape_pop(driver, search_input)
    generalinfo = scrape_generalinfo(driver, search_input)
    return [populartimesgraph,generalinfo]

