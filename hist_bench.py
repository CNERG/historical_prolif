import numpy as np
import pandas as pd
import gen_fns
import math
import re

def reformat_raw_data(file, n_header=1):
    from gen_fns import get_data
    countries, columns, raw_data = get_data(file, n_header)

    #    pursuit_cols = [0, 1, 3, 5, 7, 8, 11, 12, 13, 17, 18, 20, 22, 23]
    #    acquire_cols = [0, 2, 4, 6, 9, 10, 14, 15, 16, 17, 19, 21, 22, 24]

    #    pursuit_cols = np.empty
    #    acquire_cols = np.empty
    #    new_cols = np.empty
    
    pursuit_cols = []
    acquire_cols = []
    pursue_names = []
    acquire_names = []
    clean_names = []
    
    for c in range(len(columns)):
        if ('Country' in columns[c]):
            pass
        elif ('Pursuit_' in columns[c]):
            #          pursuit_cols.append(c)
            pursue_names.append(columns[c])
            new_str = re.sub('Pursuit_', '', columns[c])
            clean_names.append(new_str)
        elif ('Acquire_' in columns[c]):
            #           acquire_cols.append(c)
            acquire_names.append(columns[c])
        else:
            #            pursuit_cols.append(c)
            #            acquire_cols.append(c)
            pursue_names.append(columns[c])
            acquire_names.append(columns[c])
            clean_names.append(columns[c])
        print "name is", columns[c]
        
    # Column headings include 'Country', but raw_data does not
    # Must drop Country from the list of clean names
    pursue_array = raw_data[pursue_names]
    acquire_array = raw_data[acquire_names]

    pursue_array.dtype.names = clean_names
    acquire_array.dtype.names = clean_names
    
    
    #    new_str = re.sub('Pursuit_', '', columns[c])
    #            new_str = re.sub('Acquire_', '', columns[c])

#    for (row in acquire_array):
#        if (math.isnan(acquire_array['Date'][row])):


# use ma.masked_values to MAKE A MASK WHERE DATE VALUE IS NAN, then use ma.compress_rows

            
    return clean_names, pursue_array, acquire_array
            

    #TODO: Solution to filter array for pursuit:
    #http://stackoverflow.com/questions/26154711/filter-rows-of-a-numpy-array

    #TODO: STRIP OUT "Acquire" and "Pursuit" from text
    #TODO: After year, add in new column 'Status' == P, A, N (nuclear), E (explore), C (conventional) to represent that country's nuclear weapon status
    #TODO: Write a function that make just a list based on 'Status'
    #TODO: For any country without a year, add in 2015 (?)




    
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
    score_array = np.ndarray(factors.size)

    # find the relevant columns
    auth_col = raw_data["Global_Peace_Index"]
    
    
    #access a column: data[:,i]
    
    # TODO: LOOP THROUGH EACH COUNTRY (MAYBE NOT!)
    # TODO: CONVERT INDIVIDUAL COLUMNS INTO FACTOR SCORES, READ BACK A NEW CSV
 

# GDP defined in billions, mapped to a 1-10 scale
# TODO: NOT DEFINED TO ACCEPT ARRAYS!!!
# NOT CURRENTLY USED???!
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

# SOMEHOW THIS NEEDS TO INVERT RESULTS (high npt,ws == LOW SCORE)
def iso2score(npt, ws=None):
    stepA = 2
    stepB = 4
    stepC = 7
    
    all_scores = np.ndarray(npt.size)

    for i in range(npt.size):
        score = -1
        # if all agreements are with other non-nuclear states
        if (ws is None) or (ws[i] == 0) or (math.isnan(ws[i])):
            if (math.isnan(npt[i])):
                score = np.nan
            elif (npt[i] <= stepA):
                score = 1
            elif (npt[i] <= stepB):
                score = 2
            else:
                score = 3
        else:
            if (ws[i] <= stepA):
                score = 6
            elif (ws[i] <= stepB):
                score = 7
            elif (ws[i] <= stepC):
                score = 8
            else:
                score = 10

        all_scores[i] = score

    return all_scores


# Use Global Peace Index to convert both domestic and external stability into
# a conflict score

# *** NOT DEFINED FOR VALUES BETWEEN 2.5 and 3!!!
def conflict2score(gpi_array):
    stepA = 1.5
    stepB = 2
#    step3 = 2.5
    stepC = 3
    stepD = 3.5

    all_scores = np.ndarray(gpi_array.size)

    for i in range(gpi_array.size):
        gpi_val = gpi_array[i]
        score = -1

        if (math.isnan(gpi_val)):
            score = np.nan
        elif (gpi_val < stepA):
            score = 2
        elif (gpi_val < stepB):
            score = 4
        elif (gpi_val < stepC):
            score = 6
        elif (gpi_val < stepD):
            score = 8
        else:
            score = 10

        all_scores[i] = score
        
    return all_scores

# Fraction of GDP spent on military
def mil2score(mil_gdp):
    stepA = 1
    stepB = 2
    stepC = 3
    stepD = 5

    all_scores = np.ndarray(mil_gdp.size)
    
    for i in range(mil_gdp.size):
        score = -1
        if (math.isnan(mil_gdp[i])):
            score = np.nan
        elif (mil_gdp[i] < stepA):
            score = 1
        elif (mil_gdp[i] < stepB):
            score = 2
        elif (mil_gdp[i] < stepC):
            score = 4
        elif (mil_gdp[i] < stepD):
            score = 7
        else:
            score = 10

        all_scores[i] = score

    return all_scores


# Convert number of reactors to a score
# ** DOES THIS INCLUDE RESEARCH OR ONLY COMMERCIAL?
# ** HOW TO DEAL WITH PLANNED VS BUILT???
#def react2score(n_planned, n_built=None):
def react2score(n_react):
    step0 = 0.0
    stepA = 1.0
    stepB = 3.0
    stepC = 7.0
       
    all_scores = np.ndarray(n_react.size)
    
    for i in range(n_react.size):
        score = -1
        print n_react[i]
        if (math.isnan(n_react[i])):
            score = np.nan
        elif (n_react[i] == step0):
            score = 0
        elif (n_react[i] <= stepA):
            score = 1
        elif (n_react[i] <= stepB):
            score = 4
        elif (n_react[i] <= stepC):
            score = 7
        else:
            score = 10

        all_scores[i] = score

    return all_scores


# convert network (defined by intuition as small=1, medium=2, large=3) into
# a factor score on 1-10 scale.
# IS THIS IMPLEMENTED CONSISTENT WITH SPREADSHEET??
def network2score(sci_val):

    all_scores = np.ndarray(sci_val.size)
    
    for i in range(sci_val.size):
        score = -1
        if (math.isnan(sci_val[i])):
            score = np.nan
        elif (sci_val[i] == 1):
            score = 1
        elif (sci_val[i] == 2):
            score = 5
        else:
            score = 10

        all_scores[i] = score

    return all_scores


# 
# ** HOW DO THESE DATA SPIT OUT to prolif and non-prolif?
# WHAT IF A COUNTRY HAS MORE THAN 6 alliacnes?
def alliance2score(non_prolif, prolif=0):
    stepA = 2
    stepB = 4
    stepC = 6
    
    all_scores = np.ndarray(non_prolif.size)
    
    for i in range(non_prolif.size):
        score = -1
        if (prolif is None) or (prolif[i] == 0) or (math.isnan(prolif[i])):
            if (math.isnan(non_prolif[i])):
                score = np.nan
        if (prolif[i] == 0):
            if (non_prolif[i] <= stepA):
                score = 1
            elif (non_prolif[i] <= stepB):
                score = 2
            else:
                score = 3
        else:
            if (prolif[i] <= stepA):
                score = 5
            elif (prolif[i] <= stepB):
                score = 6
            else:
                score = 7

        all_scores[i] = score

    return all_scores

        