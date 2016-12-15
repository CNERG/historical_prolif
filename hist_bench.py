import numpy as np
import pandas as pd
import gen_fns
import math
import re
import csv

def reformat_raw_data(file, n_header=1, outfile=None):
    from gen_fns import get_data
    from numpy.lib.recfunctions import append_fields
    
    countries, columns, raw_data = get_data(file, n_header, named_struct=True)

    pursue_names = []
    acquire_names = []
    clean_names = []

    status = np.full(len(countries), 0)
    raw_data = append_fields(raw_data, 'Status', status)

    cols = raw_data.dtype.names
    order = range(0, len(cols) - 1)
    order.insert(2,len(cols) - 1)
    data = raw_data[[cols[i] for i in order]]
    cols = data.dtype.names
    
    for c in range(len(cols)):
#        if ('Country' in cols[c]):
#            pass
        if ('Pursuit_' in cols[c]):
            pursue_names.append(cols[c])
            new_str = re.sub('Pursuit_', '', cols[c])
            clean_names.append(new_str)
        elif ('Acquire_' in cols[c]):
            acquire_names.append(cols[c])
        else:
            pursue_names.append(cols[c])
            acquire_names.append(cols[c])
            clean_names.append(cols[c])
        
    pursue_array = data[pursue_names]
    acquire_array = data[acquire_names]
    
    acquire_mask = np.isnan(acquire_array['Acquire_Date'])
    acquire_states = countries[~acquire_mask]
    acquire_array = acquire_array[~acquire_mask]

    pursue_mask = np.isnan(pursue_array['Pursuit_Date'])
    conven_array = pursue_array[pursue_mask]
    conven_states = countries[pursue_mask]
    pursue_array = pursue_array[~pursue_mask]
    pursue_states = countries[~pursue_mask]

    # For countries that have not pursued, date should be 2015
    conven_array['Pursuit_Date'] = 2015
    pursue_array['Status'] = 2
    acquire_array['Status'] = 3

    pursue_array.dtype.names = clean_names
    pursue_array.mask.dtype.names = clean_names
    acquire_array.dtype.names = clean_names
    acquire_array.mask.dtype.names = clean_names
    conven_array.dtype.names = clean_names
    conven_array.mask.dtype.names = clean_names


    final_states = np.hstack((pursue_states, acquire_states, conven_states))
    final_data = np.hstack((pursue_array, acquire_array, conven_array))
    
    header ='Country' + '\t' + ('\t'.join(map(str,final_data.dtype.names)))

    if (outfile != None):
        with open(outfile, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([header])
            i = 0
            for comp in final_data.compressed():
                cur_line = final_states[i]
                for c in range(len(comp)):
                    val = comp[c]
                    if (c <= 1):
                        val = int(val)
                    cur_line = cur_line + '\t' + str(val)
                writer.writerow([cur_line])
                i+=1
                
    return final_states,final_data

    
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
def raw_to_factor_scores(infile, n_head=1, outfile=None):
    from gen_fns import get_data
    countries, col_names, raw_data = get_data(infile, n_header = n_head,
                                              named_struct=True)
    
    factors = {
        "Reactors": [react2score, raw_data['Reactors']],
        "Mil_Iso": [alliance2iso_score, [raw_data['NonProlif_Alliance'],
                                         raw_data['Prolif_Alliance']]],
        "Enrich": [enrich2score, raw_data['Enrichment']],
        "U_Res": [ures2score, raw_data['UReserves']],
        "Sci_Net": [network2score, raw_data['Scientific_Network']],
        "Conflict": [gpi2conflict_score, raw_data['Polity_Index']],
#        "Auth": [],
        "Mil_Sp": [mil_sp2score, raw_data['Military_GDP']]
        }

    score_columns = []
    i = 0
    
    for key in factors:
        score_columns.append(key)
        fn, inputs = factors[key]
        scores = fn(inputs)
        if (i == 0):
            all_scores = scores
        else:
            all_scores = np.column_stack((all_scores, scores))
        i+=1

    # TODO: CONVERT INDIVIDUAL COLUMNS INTO FACTOR SCORES, READ BACK A NEW CSV
    # Write out column header, states, scores to file.

    header ='Country' + '\t' + ('\t'.join(map(str,score_columns)))

    if (outfile != None):
        with open(outfile, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([header])
            for row in range(len(all_scores)):
                cur_line = countries[row]+'\t'+('\t'.join(map(str,all_scores[row])))
                writer.writerow([cur_line])
    
    return factors, score_columns, all_scores
    

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
# THIS IS NOT CURRENTLY USED IN PE
def bilateral2score(npt, ws=None):
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


#
# Use Global Peace Index to define a conflict score
# (includes both domestic and external stability)
# Institute for Economics & Peace Global Peace Index
# http://economicsandpeace.org/wp-content/uploads/2015/06/Global-Peace-Index-Report-2015_0.pdf
#
def gpi2conflict_score(gpi_array):
    stepA = 1.5
    stepB = 2
    stepC = 2.5
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

#
# Fraction of GDP spent on military
# World Bank http://data.worldbank.org/indicator/MS.MIL.XPND.GD.ZS
#
def mil_sp2score(mil_gdp):
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
# Straight sum of alliances with poliferant and non_proliferant states
# Rice University Database http://atop.rice.edu/search
#
# HOW TO COMBINE SCORES IS STILL UNCLEAR
def alliance2iso_score(all_alliances):
    stepA = 2
    stepB = 4
    step2 = 3
    
    non_prolif = all_alliances[0]
    prolif = all_alliances[1]
    
    all_scores = np.ndarray(non_prolif.size)
        
    tot_prolif = non_prolif + prolif

    # WHAT HAPPENS IF NON_PROLIF IS NAN BUT PROLIF IS A NUMBER??
    for i in range(non_prolif.size):
        score = -1
        if (math.isnan(prolif[i])) and (math.isnan(non_prolif[i])):
                score = np.nan
        elif (non_prolif[i] <= stepA):
                score = 1
        elif (non_prolif[i] <= stepB):
                score = 2
        else:
                score = 3
        if (prolif[i] != 0) and (not math.isnan(prolif[i])):
            if (prolif[i] >= step2):
                score = score + 3
            else:
                score = score + prolif[i]

        all_scores[i] = score

    return all_scores


#
# Polity IV Series http://www.systemicpeace.org/inscrdata.html
#
def polity2auth_score(polity):
    scores = polity
    return scores

# 
# Fuhrmman http://www.matthewfuhrmann.com/datasets.html
# If any enrichment or reprocessing capability then 10, otherwise 0
#
def enrich2score(enrich):
    scores = enrich
    return scores

#
# If any U reserves than 10, otherwise 0
# OECD U report
# https://www.oecd-nea.org/ndd/pubs/2014/7209-uranium-2014.pdf
#
def ures2score(ures):
    scores = ures
    return scores