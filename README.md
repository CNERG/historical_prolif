# historical_prolif


Analyzing Historical Data
--------------------------
To Reformat Raw Data (in python):

import hist_bench
from hist_bench import reformat_raw_data
states, data = reformat_raw_data(file,n_header=1,outfile="filename")

XSLS Spreadsheet notes (these are resolved in the clean_raw_data file)
- Negative dates indicate the country 'Explored' a weapons program
- Any negative Conflict Intensity indicates a coalition war, which gets
downcoded in our analysis to be a 1 instead of a 2
- Any negative Number of Unique Conflicts indicates that an additional conflict
has been added beyond the Upsala database to indicate non-armed (tense) conflict

Status Coding
-------------
    # -1 present data for a state that unsucessfully pursued
    # 0 present data for never-pursued (has only 'conventional weapons')
    # 1 historical data for explored
    # 2 historical data for pursued
    # 3 historical data for acquired



Batch-Analysis of Simulations
------------------------------
(starting from the directory where you have the input file)
~/git/historical_prolif/run_batch_sims.sh input_file.xml

Then use Python to create a text file summarizing results:

~/mbmcgarry $ python
>>> import calc_stats
>>> from calc_stats import first_prolif_qty
>>> first_prolif_qty(‘dir_path', [’Time’,’EqnVal’, ‘Conflict’], 'myout.txt')

