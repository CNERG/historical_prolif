import numpy as np
import pandas as pd
import gen_fns
   
def calc_pursuit(raw_data, weights):
    final_vals = []
    weighted_factors = weights*raw_data
    for i in range(raw_data.shape[0]):
        val = weighted_factors[i].sum()
        final_vals.append(round(val,4))
    return final_vals


# Weapon states and their acquire date
def get_nws():
    nws = {}
    nws["China"] = 1964
    nws["France"] = 1960
    nws["India"] = 1988
    nws["Israel"] = 1969
    nws["N Korea"] = 2006
    nws["Pakist"] = 1987
    nws["S Afric"] = 1979
    nws["UK"] = 1952
    nws["US"] = 1945
    nws["USSR"] = 1949

    return nws

# States that pursued and their pursuit date
# (from google doc: Main Prolif Spreadsheet, Dec-5-2016)
def get_pursue():
    pursues = {}
    pursues["Argent"] = 1978
    pursues["Austral"] = 1961
    pursues["Brazil"] = 1978
    pursues["China"] = 1955
    pursues["Egypt"] = 1965
    pursues["France"] = 1954
    pursues["India"] = 1964
    pursues["Iran"] = 1985
    pursues["Iraq"] = 1983
    pursues["Israel"] = 1960
    pursues["Libya"] = 1970
    pursues["N Korea"] = 1980
    pursues["S Korea"] = 1970
    pursues["Pakist"] = 1972
    pursues["S Afric"] = 1974
    pursues["Syria"] = 2000
    pursues["UK"] = 1947
    pursues["US"] = 1939
    pursues["USSR"] = 1945

    return pursues

# From a matched pair of numpy arrays containing countries and their pursuit scores,
# make a new array of the pursuit scores for countries that succeeded
def get_prolif_pe(countries, pes):
    prolif_pes = []
    prolif_st = []
    proliferants = get_prolif()
    for i in range(len(countries)):
        curr_state = countries[i]
        if curr_state in proliferants:
            prolif_pes.append(pes[i])
            prolif_st.append(curr_state)
    return(prolif_st, prolif_pes)

# From a matched pair of numpy arrays containing countries and their pursuit
# scores, make a new array of the scores for the subset of countries that
# actually chose to pursue and/or succeeded
def get_pes(all_countries, pes, status):
    pursue_pes = []
    pursue_st = []
    if (status == "Pursue"):
        states = get_pursue()
    elif (status == "Prolif"):
        states = get_nws()
    else:
        return "DO YOU WANT PURSUIT OR PROLIFERANTS?"
    for i in range(len(all_countries)):
        curr_state = all_countries[i]
        if curr_state in states:
            pursue_pes.append(pes[i])
            pursue_st.append(curr_state)
    return(pursue_st, pursue_pes)


# Read in the tsv for raw data of all countries, output a tsv with the data
# converted into scores and appropriate columns replaced.
def raw_to_factor_scores(infile, n_head=1):
    from gen_fns import get_data
    countries, col_names, raw_data = get_data(infile, n_head)

    factors = np.array(["Auth", "Reactors", "Enrich", "U_Res",
                        "Sci_Net", "Mil_Iso", "Conflict", "Mil_Sp"])
    score_array = np.ndarray(0, factors.size + 1)

    # find the relevant columns
    auth_col = raw_data["Global_Peace_Index"]
    
    
    #access a column: data[:,i]

    
# TODO: LOOP THROUGH EACH COUNTRY (MAYBE NOT!)
# TODO: CONVERT INDIVIDUAL COLUMNS INTO FACTOR SCORES, READ BACK A NEW CSV
 

# GDP defined in billions, mapped to a 1-10 scale
def gdp2score(gdp_val):
    step0 = 1
    step1 = 25
    step2 = 50
    step3 = 100
    step4 = 200
    step5 = 500
    step6 = 1000
    step7 = 2000
    step8 = 10000

    score = -1
    
    if (gdp_val < step0):
        score = 0
    elif (gdp_val < step1):
        score = 1
    elif (gdp_val < step2):
        score = 2
    elif (gdp_val < step3):
        score = 3
    elif (gdp_val < step4):
        score = 5
    elif (gdp_val < step5):
        score = 7
    elif (gdp_val < step6):
        score = 8.5
    elif (gdp_val < step7):
        score = 9
    elif (gdp_val < step8):
        score = 9.5

    return score


# Bilateral agreements converted to score
# If only with non-nuclear states (npt), score is lower
# If with nuclear states (nuclear umbrella), then only count these

def agreement2score(npt, non_npt=0):
    stepA = 2
    stepB = 4
    stepC = 7

    score = -1
    # if all agreements are with other non-nuclear states
    if (non_npt == 0):
        if (npt <= stepA):
            score = 1
        elif (npt <= stepB):
            score = 2
        elif (npt <= stepC):
            score = 3
    else:
        if (non_npt <= stepA):
            score = 6
        elif (non_npt <= stepB):
            score = 7
        elif (non_npt <= stepC):
            score = 8
        else:
            score = 10

    return score


# Use global peace index to convert both domestic and external stability into
# a conflict score

# *** NOT DEFINED FOR VALUES BETWEEN 2.5 and 3!!!
def peace2score(gpi_array):
    stepA = 1.5
    stepB = 2
#    step3 = 2.5
    stepC = 3
    stepD = 3.5

    all_scores = np.array(gpi_array.size) #size(gpi_array)

    for ind in range(gpi_array.size):
        print "ind", ind
        gpi_val = gpi_array[ind]
        score = -1
        
        if (gpi_val < stepA):
            score = 2
        elif (gpi_val < stepB):
            score = 4
        elif (gpi_val < stepC):
            score = 6
        elif (gpi_val < stepD):
            score = 8
        else:
            score = 10

        print "score ", score
        all_scores[ind] = score
        
    return all_scores

# Fraction of GDP spent on military
def mil2score(mil_gdp):
    stepA = 1
    stepB = 2
    stepC = 3
    stepD = 5

    score = -1
    if (mil_gdp < stepA):
        score = 1
    elif (mil_gdp < stepB):
        score = 2
    elif (mil_gdp < stepC):
        score = 4
    elif (mil_gdp < stepD):
        score = 7
    else:
        score = 10

    return score


# Convert number of reactors to a score
# ** DOES THIS INCLUDE RESEARCH OR ONLY COMMERCIAL?
# ** HOW TO DEAL WITH PLANNED VS BUILT???
def react2score(n_planned, n_built=0):
    stepA = 3
    stepB = 7

    score = -1
    
    if (n_built == 0):
        if (n_planned <= stepA):
            score = 1
        else:
            score = 2
    else:
        if (n_built <= stepA):
            score = 4
        elif (n_built <= stepB):
            score = 7
        else:
            score = 10

    return score


# convert network (defined by intuition as small=1, medium=2, large=3) into
# a factor score on 1-10 scale.
# IS THIS IMPLEMENTED CONSISTENT WITH SPREADSHEET??
def network2score(sci_val):
    score = -1

    if (sci_val == 1):
        score = 1
    elif (sci_val == 2):
        score = 5
    else:
        score = 10

    return score


# 
# ** HOW DO THESE DATA SPIT OUT to prolif and non-prolif?
# WHAT IF A COUNTRY HAS MORE THAN 6 alliacnes?
def alliance2score(non_prolif, prolif=0):

    stepA = 2
    stepB = 4
    stepC = 6
    
    score = -1
    if (prolif == 0):
        if (non_prolif <= stepA):
            score = 1
        elif (non_prolif <= stepB):
            score = 2
        else:
            score = 3
    else:
        if (prolif <= stepA):
            score = 5
        elif (prolif <= stepB):
            score = 6
        else:
            score = 7

    return score

        