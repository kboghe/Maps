import pandas as pd

####################################################################################

def appending_poptimes(populartimesgraph,general_popdatacol,general_popdata):
    for d in (general_popdata, populartimesgraph):  # you can list as many input dicts as you want here
        for key, value in d.items():
            general_popdatacol[key].append(value)
    return general_popdatacol

##################################################################################

def dataframe_poptimes(general_popdatacol):
    #create dataframe from popular times data#
    for key, value in general_popdatacol.items(): #flatten the dictionary of popular times data
        general_popdatacol[key] = (sum(value,[]))
    general_popdatacol = pd.DataFrame.from_dict(general_popdatacol)
    return general_popdatacol
