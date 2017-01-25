# historical_prolif


Analyzing Historical Data
--------------------------
To Reformat Raw Data (in python):

import hist_bench
from hist_bench import reformat_raw_data
states, data = reformat_raw_data(file,n_header=1,outfile="filename")

Any negative dates indicate the country 'Explored' a weapons program, therefore
change their "Status" to 1.


Batch-Analysis of Simulations
------------------------------
(starting from the directory where you have the input file)
~/git/historical_prolif/run_batch_sims.sh input_file.xml

Then use Python to create a text file summarizing results:

~/mbmcgarry $ python
>>> import calc_stats
>>> from calc_stats import first_prolif_qty
>>> first_prolif_qty(‘dir_path', [’Time’,’EqnVal’, ‘Conflict’], 'myout.txt')

