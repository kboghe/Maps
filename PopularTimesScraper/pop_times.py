from random import randint
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import time
from selenium.webdriver.common.action_chains import ActionChains

def scrape_pop(driver,search_input):

    check_popular_times = driver.find_elements_by_class_name("section-popular-times-graph")  # look for the "popular times" element on the page
    popular_times_available = len(check_popular_times)  # check whether the place is popular enough to have "popular times" enabled.
    percentage_list, hour_list, day_list, station, name_google, hours_in_day,id, url = ([] for i in range(8))

    ############
    ### url ####
    ############
    url_element = driver.current_url

    ##################
    ### id Google ####
    ##################
    time.sleep(5)
    try:
        id_element = driver.find_element_by_css_selector('span[class*="plus-code"]').find_element_by_xpath('../..').text
    except NoSuchElementException:
        id_element = "no id available"

    ###############################
    # SCRAPING POPULAR TIMES GRAPH#
    ###############################

    if popular_times_available > 0:  # if you have found the popular times graph (length of elements found is greater than zero).
        print("Popular times available! Scraping...")  # print a message

        table_count = 0  # number of day to scrape
        count_days = 0  # days already scraped

        #####################
        # define current day#
        #####################

        day_list_pick = ['maandag','dinsdag','woensdag','donderdag','vrijdag','zaterdag','zondag']
        day_of_week = driver.find_element_by_css_selector('div[class*="goog-menu-button-caption"]') # look for the element containing the name of the CURRENT day
        ActionChains(driver).move_to_element(day_of_week).perform()
        day_of_week = day_of_week.text
        index_day = day_list_pick.index(day_of_week)

        ##############
        # access table#
        ##############

        while table_count < 7:  # as long as the table count is less than 7 (so as long as you haven't scraped every day of the week: from day 0 to 6)
            today_table = driver.find_elements_by_class_name("section-popular-times-graph")[table_count]  # retrieve the table of that specific day (we'll update the 'table_count' later
            today_table_bs = BeautifulSoup(today_table.get_attribute('innerHTML'),'lxml')  # #load it into Beautifulsoup

            ##################
            # exceptions check#
            ##################

            check_availability_day = today_table_bs.find_all("span", string=re.compile(r"Nog niet voldoende gegevens voor (.)*"))  # check whether a particular day has not enough info for calculating the popular times
            check_closing_day = today_table_bs.find_all("span", string=re.compile(r"Gesloten op (.)*"))  # check whether a station is labeled as 'closed' during a particular day

            if (len(check_availability_day) == 1) or (len(check_closing_day) > 0):  # if one of these two messages are displayed...
                bars_length = 1  # find out how many hours are displayed in a day for this station, even if there are no hours available for 'today'
                while bars_length < 2:  # there should be AT LEAST two hours available in a day where popular times are available. So as long as this is NOT the case...
                    try:  # try to...
                        random_day = randint(0, 6)  # pick a random day of the week...
                        check_bars = driver.find_elements_by_class_name("section-popular-times-graph")[random_day]  # ...and acces the popular times of this randomly chosen day
                    except NoSuchElementException:  # if you haven't found a table for this day, start the loop again (and pick another random day), until you found a suitable one
                        continue  # restart te loop
                    else:  # if you have found a particular day
                        check_bars_bs = BeautifulSoup(check_bars.get_attribute('innerHTML'),'lxml')  # load the table in Beautifulsoup
                        bars_check = check_bars_bs.find_all("div", attrs={"aria-label": True,"class": "section-popular-times-bar"})  # retrieve the bar elements of that day
                        bars_length = len(bars_check)  # store the amount of bars displayed

                if len(check_availability_day) > 0:  # if this day is labeled as not popular enough to display popular times#
                    message = "not enough location data available for this day"  # formulate a message
                if len(check_closing_day) > 0:  # if this day is labeled as closed on this particular day
                    message = "day marked as closed"  # formulate a message

                percentage_list.extend([message])  # repeat this message X amount of times (length of bars)
                hour_list.extend([message])  # repeat this message X amount of times (length of bars)
                day_list.extend([day_list_pick[index_day]])

                ##########################
                # retrieve bar information#
                ##########################

            if (len(check_availability_day) == 0) and (len(check_closing_day) == 0):  # if this day isn't closed and has enoguh information to display popular times...
                bars = today_table_bs.find_all("div", attrs={"aria-label": True,"class": "section-popular-times-bar"})  # find all the popular times bars for this day

                for bar in bars:  # for each element in these bars (thus: for each bar)...
                    bars_length = len(bars)
                    info = bar.get('aria-label')  # get the aria label, which contains the 'busy percentage' (0-100%) we're looking for!
                    info = re.sub('Momenteel [0-9]{1,2}% van maximale drukte, normaal ', '', info)  # remove all the additional text around that percentage. This is only necessary if you're scraping the current hour and day of the week
                    percentage = info.split('%')[0]  # split the label on % and only keep everything BEFORE the split-sign (so 23% ==> 23)
                    percentage_list.append(percentage)  # append this percentage to a list
                    try:  # Then, extract the hour information (0-24)
                        hour = info.split("om ")[1]  # split the info on "om" ('on') and keep eveything AFTER "om"
                        hour = re.sub(":00.", "", hour)  # delete ":00" (so 07:00 --> 07)
                        hour = hour.lstrip("0")  # remove zeros from the left (so  07 --> 7)
                        emptystring = ""  # define an empty string
                        if hour is emptystring:  # if the hour is empty
                            hour = 0  # we've 'accidentally' deleted midnight (because these are all zeros). Set the hour to zero then.
                    except IndexError as error:  # if you haven't found the hour value
                        hour = previous_value + 1  # take the previous value and add 1
                        previous_value = int()  # and make the "previous value" value empty again
                    finally:  # finally, whatever you've done before...
                        previous_value = int(hour)  # convert the "hour" value to an integer (numeric)
                        hour_list.append(hour)  # and append it to our list

                day_list.extend([day_list_pick[index_day]]*bars_length)

            table_count = table_count + 1  # we've finished scraping a particular day. On to the next one
            index_day = index_day + 1
            if index_day > 6:
                index_day = 0
        table_count = 0  # if you've finished scraping all seven days (0-6), set the table counter back to zero (for scraping our next place)
        print("Done!\n")  # print a message

        ##################
        # add search input#
        ##################
        station.extend([search_input] * len(day_list))  # add it (bars in one day * 7 days) times

        ###########################
        # add title of google place#
        ###########################
        title = driver.find_elements_by_class_name("section-hero-header-title-title")[0]
        title = BeautifulSoup(title.get_attribute('innerHTML'), 'lxml').text
        name_google.extend([title] * len(day_list))  # add it (bars in one day * 7 days) times

        hours_in_day.extend([bars_length] * len(day_list))  # add the amount of hours in a day

        ##########
        # add url#
        ##########
        url.extend([url_element] * len(day_list))

        ################
        # add id Google#
        ################
        id.extend([id_element] * len(day_list))

    ######################################
    # NO POPULAR TIMES AVAILABLE FOR PLACE#
    ######################################

    if popular_times_available == 0:
        print("Sorry, no popular times available...\n")  # print a message
        nothing_available = list(["no popular times available!"])  # formulate a message to add to our general dataframe..
        station.append(search_input)  # and append it to our dataset#
        title = driver.find_elements_by_class_name("section-hero-header-title-title")[0].text
        name_google = list([title])
        id = list([id_element])
        url = list([url_element])
        hours_in_day = percentage_list = hour_list = day_list = nothing_available

    dict_poptimes = {'url':url,'search input': station, 'google maps name': name_google,'id':id, 'hours in day': hours_in_day,
                     'percentage busy': percentage_list, 'hour list': hour_list, 'day list': day_list}
    return dict_poptimes