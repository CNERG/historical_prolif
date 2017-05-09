import numpy as np
import pandas as pd
import gen_fns
import math
import re
import csv
import correlation_matrix as co


#
# reformat_raw_data
#
# Takes compiled data on historical proliferation contributers from xlsx
# spreadsheet (final_hist_data.xlsx) and reformats. xlsx file has a single
# row for each country with separate data for a 'pursue date' and an 'acquire
# 'date'.  These are split out so that each state has a unique row entry for
# every year for which we have data. Nuclear Weapon states have an entry when
# they began pursuing and another when they acquired. States that explored or
# pursued have an entry for that year as well as an entry for 2015. States
# that never pursued have only an entry for 2015.
# A 'Status' column in output codes the action of the state in the given year
# (Never/Explore/Pursue/Acquire). Coding details available inline.
#
# Input
#    File:       tab-separated-file dropped straight from xlsx spreadsheet
#    (n_header): number of extra header lines to be skipped from spreadsheet
#    (outfile):  name of desired output file, written to directory you're
#                running python from
# Output
#    States:     Array of states for each entry of the file database
#    Data:       structured array of historical data for each state at time
#                indicated by 'Date' 
#
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
        
    # all countries, data split into pursue-relevant or acquire-relevant
    pursue_array = data[pursue_names]
    acquire_array = data[acquire_names]

    no_acquire_mask = np.isnan(acquire_array['Acquire_Date'])
    conven_mask = np.isnan(pursue_array['Pursuit_Date'])
    explore_mask = (pursue_array['Pursuit_Date'] < 0)
    pursue_only_mask = (np.isnan(acquire_array['Acquire_Date'])) & (~(np.isnan(pursue_array['Pursuit_Date'])) & (pursue_array['Pursuit_Date'] > 0))

    # states that pursued (_init_) and successfully acquired
    acquire_states = countries[~no_acquire_mask]
    acquire_final_array = acquire_array[~no_acquire_mask]
    acquire_init_array = pursue_array[~no_acquire_mask]

    # states that never pursued and have only conventional weapons
    conven_array = pursue_array[conven_mask]
    conven_states = countries[conven_mask]

    # states that explored NW but ultimately did not pursue
    explore_array = pursue_array[explore_mask]
    explore_present_array = acquire_array[explore_mask]
    explore_states = countries[explore_mask]

    # states that pursued but did not succeeed in acquiring
    pursue_only_array = pursue_array[pursue_only_mask]
    pursue_present_array = acquire_array[pursue_only_mask]
    pursue_states = countries[pursue_only_mask]

    # Status
    # -1 present data for a state that unsucessfully pursued
    # 0 present data for never-pursued (has only 'conventional weapons')
    # 1 historical data for explored
    # 2 historical data for pursued
    # 3 historical data for acquired
    acquire_init_array['Status'] = 2
    acquire_final_array['Status'] = 3
    conven_array['Status'] = 0
    pursue_only_array['Status'] = 2
    pursue_present_array['Status'] = -1
    explore_array['Status'] = 1
    explore_present_array['Status'] = 0
    
    conven_array['Pursuit_Date'] = 2015
    explore_array['Pursuit_Date'] = abs(explore_array['Pursuit_Date'])
    explore_present_array['Acquire_Date'] = 2015
    pursue_present_array['Acquire_Date'] = 2015
    
    acquire_final_array.dtype.names = clean_names
    acquire_final_array.mask.dtype.names = clean_names
    acquire_init_array.dtype.names = clean_names
    acquire_init_array.mask.dtype.names = clean_names
    conven_array.dtype.names = clean_names
    conven_array.mask.dtype.names = clean_names
    pursue_only_array.dtype.names = clean_names
    pursue_only_array.mask.dtype.names = clean_names
    pursue_present_array.dtype.names = clean_names
    pursue_present_array.mask.dtype.names = clean_names
    explore_array.dtype.names = clean_names
    explore_array.mask.dtype.names = clean_names
    explore_present_array.dtype.names = clean_names
    explore_present_array.mask.dtype.names = clean_names

    
    final_states = np.hstack((conven_states,
                              explore_states,
                              explore_states,
                              pursue_states,
                              acquire_states,
                              acquire_states,
                              pursue_states))
    final_data = np.hstack((conven_array,
                            explore_present_array,
                            explore_array,
                            pursue_only_array,
                            acquire_init_array,
                            acquire_final_array,
                            pursue_present_array))
    
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


#
# calc_weights
#
# Given a tab separated input file with the following columns, use partial
# component analysis to determine the relative importance of each factor
# In:
#    filename:   tab-separated input file with factor scores for each state
#                columns: Country, Date, Status, Factor1, Factor2, ....
#    mn_status:  min value of nuclear weapons status for state to be considered
#                in analysis (-1 = gave up weapons program, 0 = never pursued,
#                1 = explored, 2 = pursued, 3 = acquired)
#    mx_status:  max value of weapons status to be considered
#    correl_min: weights below this number are rescaled to zero as they are
#                not significant (including negative correlations)
#
# Out:
#    weights:    relative importance of each factor from the input file. Weights
#                sum to 1 and cannot be negative.
#
def calc_weights(filename, mn_status=0, mx_status=2, correl_min = 1e-6):
    data_file = open(filename, 'r')
    full_matrix = np.loadtxt(data_file, skiprows=1,usecols=(2,3,4,5,6,7,8,9,10))
    relevant_mask = ((full_matrix[:,0] >= mn_status) &
                     (full_matrix[:,0] <= mx_status))
    matrix = full_matrix[relevant_mask]

    cor = co.Cor_matrix(matrix)
    factor_vals = np.array(cor[0,1:])[0]
    factor_vals[factor_vals < correl_min] = 0
    f_tot = factor_vals.sum()
    weights = factor_vals/f_tot  # normalize weights to sum to one

    return weights


    
#
# calc_pursuit
#
# Calculates 0-10 scale pursuit scores for historical data using factor
# weighting from Baptiste's correlation analysis.
#
# In:
#     raw_data:   np.array of value for each factor on a 0-10 scale
#     weights:    np.array of factor weights (from correlation analysis)
# Out:
#     final_vals: List of pursuit equation values in same order as input data
#                 (order: Auth, Mil_Iso, Reactor, En_Repr, Sci_Net, Mil_Sp,
#                 Conflict, U_Res)
#
def calc_pursuit(raw_data, weights):
    final_vals = []
    weighted_factors = weights*raw_data
    for i in range(raw_data.shape[0]):
        val = weighted_factors[i].sum()
        final_vals.append(round(val,4))
    return final_vals


# Map of nuclear weapon states and their acquire date
def get_nws():
    nws = {}
    nws["China"] = 1964
    nws["France"] = 1960
    nws["India"] = 1974
#    nws["India"] = 1988  # This was the Way coding but not first detonation
    nws["Israel"] = 1969
    nws["N-Korea"] = 2006
    nws["Pakist"] = 1987
    nws["S-Afric"] = 1979
    nws["UK"] = 1952
    nws["US"] = 1945
    nws["USSR"] = 1949

    return nws

#
# time_to_acquire
#
# Returns a dictionary of countries that pursued and how long it took them to
# succeed. Countries that never acquired are listed with a negative number that
# indicates the time elapsed from beginning of pursuit to 2015
#
# In: (none)
# Out:
#     t2acq: Dictionary of how long it took state to acquire nuclear weapon
#
def time_to_acquire():
    t2acq = {}
    t2acq["Argent"] = -37
    t2acq["Austral"] = -54
    t2acq["Brazil"] = -37
    t2acq["China"] = 9
    t2acq["Egypt"] = -50
    t2acq["France"] = 6
    t2acq["India"] = 10
    t2acq["Iran"] = -30
    t2acq["Iraq"] = -32
    t2acq["Israel"] = 9
    t2acq["Libya"] = -45
    t2acq["N-Korea"] = 26
    t2acq["S-Korea"] = -45
    t2acq["Pakist"] = 15
    t2acq["S-Afric"] = 5
    t2acq["Syria"] = -15
    t2acq["UK"] = 5
    t2acq["US"] = 3
    t2acq["USSR"] = 4
    return t2acq


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
    pursues["N-Korea"] = 1980
    pursues["S-Korea"] = 1970
    pursues["Pakist"] = 1972
    pursues["S-Afric"] = 1974
    pursues["Syria"] = 2000
    pursues["UK"] = 1947
    pursues["US"] = 1939
    pursues["USSR"] = 1945

    return pursues

# From a matched pair of numpy arrays containing countries and their pursuit 
# scores, make a new array of the pursuit scores for countries that succeeded
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

#
# raw_to_factor_scores
#
# Read in the historical data for all states, output a tsv with the data
# converted into 0-10 scores for each of the 8 factors
#
# In:
#     infile:    tsv for historical data in clean format
#                (from reformat_raw_data) 
#     (n_head):  how many header lines to skip
#     (outfile): name of desired tab separated file for output, with row and
#                column headers
# Out: (all structures preserve order across columns)
#     countries:  array of state names that pairs with output data
#     dates:      array of date for the row of factor scores
#     status:     array with status for the row (never/explore/pursue/acquire)
#                 (status coding described in README.md)
#     columns:    list of column names for data
#     all_scores: np.array of 0-10 score for each factor
#     
def raw_to_factor_scores(infile, n_head=1, outfile=None):
    from gen_fns import get_data
    countries, col_names, raw_data = get_data(infile, n_header = n_head,
                                              named_struct=True)
    
    factors = {
        "Reactor": [react2score, [raw_data['Reactors'],
                                   raw_data['Research_Reactors']]],
        "Mil_Iso": [alliance2iso_score, [raw_data['NonProlif_Alliance'],
                                         raw_data['Prolif_Alliance']]],
        "En_Repr": [enrich2score, raw_data['Enrichment']],
        "U_Res": [ures2score, raw_data['UReserves']],
        "Sci_Net": [network2score, raw_data['Scientific_Network']],
#        "Conflict": [upsala2conflict_score, [raw_data['Unique_Conflicts'],
#                                         raw_data['Conflict_Intensity']]],
        "Conflict": [relations2conflict_score,
                     [raw_data['Weapon_Status_1'],
                      raw_data['Conflict_Relation_1'],
                      raw_data['Weapon_Status_2'],
                      raw_data['Conflict_Relation_2'],
                      raw_data['Weapon_Status_3'],
                      raw_data['Conflict_Relation_3'],
                      raw_data['Status']]],
        "Auth": [polity2auth_score, raw_data['Polity_Index']],
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

    header ='Country' + '\t' + 'Date'+ '\t' + 'Status' + '\t'+ (
        '\t'.join(map(str,score_columns)))

    if (outfile != None):
        with open(outfile, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow([header])
            for row in range(len(all_scores)):
                cur_line = countries[row]+ '\t'+ (
                    str(int(raw_data['Date'][row]))+ '\t') + (
                        str(raw_data['Status'][row]) + '\t') + (
                            ('\t'.join(map(str, all_scores[row]))))
                writer.writerow([cur_line])
    
    return countries, raw_data['Date'], raw_data['Status'], score_columns, all_scores
    

# Bilateral agreements converted to score
# If only with non-nuclear states (npt), score is lower
# If with nuclear states (nuclear umbrella), then only count these
#
# NOT CURRENTLY USED
#
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
# Global Peace Index
# (includes both domestic and external stability)
# Institute for Economics & Peace Global Peace Index
# http://economicsandpeace.org/wp-content/uploads/2015/06/Global-Peace-Index-Report-2015_0.pdf
#
# NOT USED BECAUSE NO HISTORICAL DATA
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
# 'Reactors' is commercial, 'Research_Reactors' are in a separate column,
# with negative number indicating they have only planned reactors.
# Built reactors take precedence over planned
#
# REFERENCE???
# ** Correlation analysis demonstrated that reactors are protective against
# proliferation (hypothesis that countries stable enough to run reactors
# have other mitigating factors that reduce proliferation risk)
# Therefore reactor score has been inverted so that the more reactors a country
# has the lower their pursuit score.

def react2score(all_reactors):
    step0 = 0.0
    stepA = -4.0
    stepB = -1.0
    stepC = 3.0
    stepD = 7.0

    n_react = all_reactors[0]
    n_research = all_reactors[1]
    
    all_scores = np.ndarray(n_react.size)
    
    for i in range(n_react.size):
        score = 0
        n_tot = 0
        # if there are both planned (negative) and built reactors (positive)
        # between research and commercial, use the 'built' number
        if ((n_react[i] * n_research[i]) < 0):
            n_tot = max(n_research[i], n_react[i])
        else:
            n_tot = n_research[i] + n_react[i]
            
        if (math.isnan(n_tot)):
            score = np.nan
        elif (n_tot == step0):
            score = 0
        elif (n_tot <= stepA):
            score = 2
        elif (n_tot <= stepB):
            score = 1
        elif (n_tot <= stepC):
            score = 4
        elif (n_tot <= stepD):
            score = 7
        else:
            score = 10

        all_scores[i] = 10 - abs(score)

    return all_scores

#
# upsala2conflict_score
#
# Uses number of unique conflicts * conflict intensity to determine total
# conflict score.  We have re-coded Iraq, Afghanistan, and Mali wars (2000s)
# as coalition-wars, such that for individual countries the number of deaths
# is the lower intensity coded as 1.
# Max # of unique conflicts in historical data is 3
# Conflict = 5 for neutral relationships, increases with additional conflict.
#
# From Upsala
# 
def upsala2conflict_score(all_conflict):
    neutral = 5  # for neutral relationships, score is 5
    stepC = 4

    n_conflicts = all_conflict[0]
    intensity = all_conflict[1]
    
    all_scores = np.ndarray(n_conflicts.size)
    
    for i in range(n_conflicts.size):
        score = 0
        # If intensity is (-) then conflict is a coalition, downgrade intensity
        # to -1. If n_conflict is (-) then an additional non-armed (tense)
        # conflict has been added to the data (eg Korean Armistace), (but still
        # may be coded as zero intensity)
        if ((intensity[i] < 0) or (n_conflicts[i] < 0)):
            n_tot = abs(n_conflicts[i])
        else:
            n_tot = n_conflicts[i] * intensity[i]
        if (math.isnan(n_tot)):
            score = np.nan
        elif (n_tot <= stepC):
            score = neutral + n_tot
        else:
            score = 10

        all_scores[i] = score

    return all_scores

#
# relations2conflict_score
#
# Averages individual conflict scores with up to 3 pairs of countries that
# have significant relationships (as determined by Hoffman and Buys).
# Each country has a weapons status (0,2,3) and a defined
# relationship with partner country (+1 = allies, 0 = neutral, -1 = enemies).
# Scores are determined based on those 3 values using the score_matrix 
# dictionary in lookup_conflict_val (these dictionary values are also used
# in mbmore::StateInst.cc (archetype for use with Cyclus).
# 
# In: np.array of arrays - for each target country, weapons status and
#                          relationship of each pair country,
#                          and weapon status of target country
# Out: np.array - for each target country, final conflict score (0-10 scale)
#
def relations2conflict_score(all_conflict):
    weapon_stat1 = all_conflict[0]
    conflict1= all_conflict[1]
    weapon_stat2 = all_conflict[2]
    conflict2= all_conflict[3]
    weapon_stat3 = all_conflict[4]
    conflict3= all_conflict[5]
    host_status = all_conflict[6]
    
    all_scores = np.ndarray(weapon_stat1.size)

    for i in range(all_scores.size):
        n_scores = 0
        score = 0
        if (np.isfinite(weapon_stat1[i])):
             n_scores+=1
             score+= lookup_conflict_val(host_status[i],
                                          weapon_stat1[i],
                                          conflict1[i])
        if (np.isfinite(weapon_stat2[i])):
             n_scores+=1
             score+= lookup_conflict_val(host_status[i],
                                          weapon_stat2[i],
                                          conflict2[i])
        if (np.isfinite(weapon_stat3[i])):
             n_scores+=1
             score+= lookup_conflict_val(host_status[i],
                                          weapon_stat3[i],
                                         conflict3[i])
        if (math.isnan(score) or (n_scores == 0)):
            avg_score = np.nan
        else:
            avg_score = score/n_scores

        all_scores[i] = avg_score 

    return all_scores
             

#
# lookup_conflict_val
#
# Given the relationship between 2 countries (enemy, ally, neutral), and their
# respective weapon status, look up the 0-10 score for that conflict level
# 0-10 scores based on discussion with Andy Kydd and documented here:
# https://docs.google.com/document/d/1c9YeFngXm3RCbuyFCEDWJjUK9Ovn072SpmlZU6j1qhg/edit?usp=sharing
# Same defns are used in mbmore::StateInst.cc (archetype for use with Cyclus).
# Historical countries with scores of -1 (gave up a weapons program) or
# +1 (explored but did not pursue) have been reassigned a value of 0 (never
# pursued). These gradations could be refined in future work.
#
# In: statusA  - weapons status of country A (0, 2, 3)
#     statusB  - weapons status of country B (0, 2, 3)
#     relation - relationship between country A and B (-1, 0, +1) 
#
# Out: Conflict factor score for that pair (0-10)
#
def lookup_conflict_val(statusA, statusB, relation):
    score_matrix = {
        "ally_0_0": 2,
        "neut_0_0": 2,
        "enemy_0_0": 6,
        "ally_0_2": 3,
        "neut_0_2": 4,
        "enemy_0_2": 8,
        "ally_0_3": 1,
        "neut_0_3": 4,
        "enemy_0_3": 6,
        "ally_2_2": 3,
        "neut_2_2": 4,
        "enemy_2_2": 9,
        "ally_2_3": 3,
        "neut_2_3": 5,
        "enemy_2_3": 10,
        "ally_3_3": 1,
        "neut_3_3": 3,
        "enemy_3_3": 5
    }
    
    # string is enemy if relation is -1
    reln_str = "enemy_"
    if (relation == 1):
        reln_str = "ally_"
    elif (relation == 0):
        reln_str = "neut_"
        
    first_stat = statusA
    second_stat = statusB

    #Convention - list smaller number first
    if (statusA > statusB):
        first_stat = statusB
        second_stat = statusA

    # Recode any status that is not 0,2,3
    # If a country has given up its weapon program (-1) or is only
    # 'exploring' (1) then treat them as 'never pursued' (0) for now.
    # Someday these status' could be given unique conflict values in the matrix
    if (first_stat == 1):
        first_stat = 0
    if (first_stat == -1):
        first_stat = 0
    if (second_stat == 1):
        second_stat = 0
    if (second_stat == -1):
        second_stat = 0

    reln_str += str(int(first_stat)) + "_" + str(int(second_stat))

    return score_matrix[reln_str]

    
# convert network (defined by intuition as small=1, medium=2, large=3) into
# a factor score on 1-10 scale.
#
# Technology Achievement Index
#
# REFERENCE URL??
#
def network2score(sci_val):
    stepA = 1
    stepB = 2
    stepC = 3
    
    all_scores = np.ndarray(sci_val.size)
    
    for i in range(sci_val.size):
        score = -1
        if (math.isnan(sci_val[i])):
            score = 1
        elif (sci_val[i] < stepA):
            score = 2
        elif (sci_val[i] < stepB):
            score = 4
        elif (sci_val[i] < stepC):
            score = 7
        else:
            score = 10

        all_scores[i] = score

    return all_scores

# 
# First assign a score of 0-3 based on number of alliances with non-nuclear
# states.
# Then add to that score a 5, 6, or 7 based on the number of alliances with
# nuclear states (if none then add 0).
#
# Rice University Database http://atop.rice.edu/search
#
def alliance2iso_score(all_alliances):
    np_stepA = 2
    np_stepB = 4
    p_stepA = 1
    p_stepB = 2
    p_stepC = 3

    non_prolif = all_alliances[0]
    prolif = all_alliances[1]
    
    all_scores = np.ndarray(non_prolif.size)
        
    for i in range(non_prolif.size):
        score = 0
        if (math.isnan(prolif[i])) and (math.isnan(non_prolif[i])):
                score = np.nan
        elif (non_prolif[i] <= np_stepA):
                score = 1
        elif (non_prolif[i] <= np_stepB):
                score = 2
        else:
                score = 3
        if (not math.isnan(prolif[i])):
            if (prolif[i] == p_stepA):
                score = score + 5
            elif (prolif[i] == p_stepB):
                score = score + 6
            elif (prolif[i] >= p_stepC):
                score = score + 7

        # Isolation is the inverse of amount of alliances
        all_scores[i] = 10 - score

    return all_scores


#
# Center for Systemic Peace
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
    scores = enrich*10.0
    return scores

#
# If any U reserves than 10, otherwise 0
# OECD U report
# https://www.oecd-nea.org/ndd/pubs/2014/7209-uranium-2014.pdf
#
def ures2score(ures):
    scores = ures*10.0
    return scores

