# historical_prolif

To Reformat Raw Data (in python):

import hist_bench
from hist_bench import reformat_raw_data
states, data = reformat_raw_data(file,n_header=1,outfile="filename")

Any negative dates indicate the country 'Explored' a weapons program, therfore
change their "Status" to 1.

