### add simple first hit####

#######################################################
def ind_search(driver,search_input):

    global unique_hit, first_hit
    percentage_list, hour_list, day_list, station, name_google, hours_in_day = ([] for i in range(6))

    print("Haven't found a specific location for " + search_input + ". Looking for specific page...")  # display a message

    # look for several categories in the list of options provided by Google maps#
    search_result1 = driver.find_elements_by_xpath("//span[contains(text(),'Treinstation')]")
    search_result2 = driver.find_elements_by_xpath("//span[contains(text(),'Spoorwegmaatschappij')]")
    search_result3 = driver.find_elements_by_xpath("//span[contains(text(),'ov-halte')]")
    search_result4 = driver.find_elements_by_xpath("//span[contains(text(),'Ov-station')]")
    search_result5 = driver.find_elements_by_xpath("//span[contains(text(),'Transit stop')]")

    # create a list of these elements#
    all_searches = list([search_result1, search_result2, search_result3, search_result4, search_result5])  # create a list
    non_empty_searches = list(filter(None, all_searches))  # delete the empty ones (i.e. delete the elements that were not found on the page
    number_succesful_searches = len(non_empty_searches)  # save the length of the succesfull searches (max = 5 if all types were found on the page ('treinstation','ov-halte',etc.))

    if number_succesful_searches == 1:  # if you've only found one exact match...
        need_to_pick = 0  # you don't need to pick a place from multiple options (we'll use this later)
        searches = {'search_result1': len(search_result1), 'search_result2': len(search_result2),'search_result3': len(search_result3), 'search_result4': len(search_result4),'search_result5': len(search_result5)}  # create a dictionary of the lengths of all searches
        unique_hit = max(searches, key=searches.get)  # and get the key of the search result with the greatest length. We'll click on this link later on.
        unique_hit = locals()[unique_hit][0]

    if number_succesful_searches > 1:  # if you've found more than one match...
        need_to_pick = 1  # you need to pick a place from multiple options

        # get the vertical coordinate (y coordinate) of the first element found of each place category and append this to a dictionary
        searches = dict()
        if len(search_result1) > 0:
            searches['search_result1'] = search_result1[0].location['y']
        if len(search_result2) > 0:
            searches['search_result2'] = search_result2[0].location['y']
        if len(search_result3) > 0:
            searches['search_result3'] = search_result3[0].location['y']
        if len(search_result4) > 0:
            searches['search_result4'] = search_result4[0].location['y']
        if len(search_result5) > 0:
            searches['search_result5'] = search_result5[0].location['y']

        first_hit = min(searches,key=searches.get)  # and get the key of the minimum value of this dictionary. This minimum value constitutes the first available link for one of these categories. We'll click on this link later on.
        first_hit = locals()[first_hit][0]


    if number_succesful_searches > 0:  # if you've found one or more links that match the specified categories...
        print("Bingo, I found a specific page!\n")  # display a message

        ##############
        # access place#
        ##############

        if need_to_pick == 0:  # if you did not need to pick (i.e. you only found one specific match...#
            unique_hit.click()  # click on the unique link

        if need_to_pick == 1:  # if you had to pick (i.e. you found more than one match....
            first_hit.click()  # click on the first place that matches the place categories

        print("clicked on the page!")
        individual_location_page = 1  # and save this in a new value. We'll use this later.

    else:  # if you haven't found a place that matches your place categories...
        print("Station not found!")  # display a message that no station was found
        individual_location_page = 0

    return individual_location_page

############################################################

def no_place_found(search_input):
    place_not_found = "place not found"  # and append this message to every list (we'll use these lists to create our general DataFrame later on)
    name_google = hours_in_day = percentage_list = hour_list = day_list = id = place_not_found
    dict_poptimes = {'search input': search_input, 'google maps name': name_google,'id':id, 'hours in day': hours_in_day,'percentage busy': percentage_list, 'hour list': hour_list, 'day list': day_list}
    dict_generalinfo = {'search input': search_input, 'google maps name': place_not_found, 'id': place_not_found,'category': place_not_found,
                        'address': place_not_found, 'score': place_not_found, 'reviews': place_not_found,'expense': place_not_found,
                        'extra info': place_not_found, 'maandag': place_not_found,'dinsdag': place_not_found,'woensdag': place_not_found,
                        'donderdag': place_not_found, 'vrijdag': place_not_found,'zaterdag': place_not_found, 'zondag': place_not_found}
    return [dict_poptimes,dict_generalinfo]