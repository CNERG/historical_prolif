#!/usr/bin/env python

import glob
import cymetric as cym
import pandas as pd

# make_list
#
# Make a list of all sqlite files in the directory defined by 'path'
#
def make_list(path):
    file_list = glob.glob(path + "*.sqlite")
    return file_list


# first_prolif_qty
#
# Return a list of the column value at the first incident of pursuit or acquire
# for all simulations in the directory
#
# Inputs: path:     path to directory containing simulations. Be sure path ends
#                   with a slash. eg "/home/cvt/data/run4/"
#         qty:      list of the column names from the weapon progress table in 
#                   the sqlite file to be returned. eg ['Time','Likelihood']
#         file:     name of output file to be used
#
# Outputs:
#        path+file: tab separated file with the values requested in
#                   the qty columns for all simulations in the directory.
def first_prolif_qty(path, qty, csv = None):
    file_list = make_list(path)
    qty_df=pd.DataFrame()
    for f in file_list:
         db = cym.dbopen(f)
         weapon_progress = cym.root_metric(name='WeaponProgress')
         evaluator = cym.Evaluator(db)
         frame = evaluator.eval('WeaponProgress', conds=[('Decision', '==', 1)])
         qty_df=pd.concat([qty_df,frame[:1][qty]],ignore_index=True)
         
    if (csv != None):
        qty_df.to_csv(path+csv, sep='\t')
        return
    else:
        return qty_df

# all_prolif_qty
#
# For a set of simulations in a directory, query the WeaponProgress table in
# each cyclus sqlite file (produced by mbmore::InteractRegion). Return a list
# of the column value for every incident of weapons pursuit or acquisition. 
#
# Inputs: path:     path to directory containing simulations. Be sure path ends
#                   with a slash. eg "/home/cvt/data/run4/"
#         qty:      list of the column names from the weapon progress table in 
#                   the sqlite file to be returned. eg ['Time','Likelihood']
#         eqn_type: specify if you want the pursuit times or the acquire times
#         file:     name of output file to be used
#
# Outputs:
#        path+file: tab separated file with the values requested in
#                   the qty columns for all simulations in the directory.
#        path+ 'agent_' +file: list of which prototype name correlates to 
#                   AgentId in the simulations
#
def all_prolif_qty(path, qty, eqn_type, file = None):
    file_list = make_list(path)
    qty_df=pd.DataFrame()
    agent_df=pd.DataFrame()
    for f in file_list:
         db = cym.dbopen(f)
         weapon_progress = cym.root_metric(name='WeaponProgress')
         evaluator = cym.Evaluator(db)
         frame = evaluator.eval('WeaponProgress',
                                conds=[('Decision', '==', 1),
                                       ('EqnType', '==', eqn_type)])
         qty_df=pd.concat([qty_df,frame[:][qty]],ignore_index=True)

         agent_entry = cym.root_metric(name='AgentEntry')
         evaluator2 = cym.Evaluator(db)
         agent_frame = evaluator2.eval('AgentEntry',
                                       conds=[('Kind', '==', 'Inst')])
         agent_df=pd.concat([agent_df,
                            agent_frame[:][['AgentId','Prototype']]],
                            ignore_index=True)
         
    if (file != None):
        qty_df.to_csv(path+file, sep='\t')
        agent_df.to_csv(path+'agent_'+file, sep='\t')
        return 
    else:
        return qty_df




         
                      
        