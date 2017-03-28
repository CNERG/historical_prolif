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


3/28/17
-------
PCA analysis shows that Reactors have anti-correlation to pursuit. Confirmed
that non-relevant factors can be removed from PCA analysis without affecting
other results (noreactor_test.csv has removed reactor column)



Notes on Commercial Reactor Technology
--------------------------------------
WHEN IS FIRST NON-WEAPONS STATE USE OF NUCLEAR ENERGY (COMMERCIAL OR RESEARCH?)

US - first reactor power 1957 (shippingport) [A]
   - first full commercial (Westinghouse) 1960 [B]
France - 1959 [B]
Canada - 1962 [B]
USSR  - 1964 (commissioned) [B]
Kazak - 1972

A)
B) http://www.world-nuclear.org/information-library/current-and-future-generation/outline-history-of-nuclear-energy.aspx

* Excluding all pursuits before 1966, (post_reactor.csv), reactor technology
is still anti-correlated to pursuit.





Batch-Analysis of Simulations
------------------------------
(starting from the directory where you have the input file)
~/git/historical_prolif/run_batch_sims.sh input_file.xml

Then use Python to create a text file summarizing results:

~/mbmcgarry $ python
>>> import calc_stats
>>> from calc_stats import first_prolif_qty
>>> first_prolif_qty(‘dir_path', [’Time’,’EqnVal’, ‘Conflict’], 'myout.txt')


