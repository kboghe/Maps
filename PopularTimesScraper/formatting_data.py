import pandas as pd

####################################################################################

def appending_data(data_specific, generaldata_col,general_data):
    for d in (general_data, data_specific):  # you can list as many input dicts as you want here
        for key, value in d.items():
            generaldata_col[key].append(value)
    return generaldata_col

##################################################################################

def dataframe_poptimes(general_popdatacol):
    #create dataframe from popular times data#
    for key, value in general_popdatacol.items(): #flatten the dictionary of popular times data
        general_popdatacol[key] = (sum(value,[]))
    general_popdatacol = pd.DataFrame.from_dict(general_popdatacol)
    return general_popdatacol
