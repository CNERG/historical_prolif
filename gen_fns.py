import numpy as np
import pandas as pd

# Import data from a tab separated file
# if named_struct then it returns a python structured array accessable by
# column name (but this does not allow for matrix multiplication)
def get_data(file, n_header=1, col_list=(), named_struct=False):
    row_names = np.genfromtxt(file, delimiter="\t", usecols=0, dtype=str,
                            skip_header=n_header)

    # Have to strip out the first column (of names) to get the rest of the info
    tmp = np.genfromtxt(file, delimiter="\t", names=True,
                        skip_header=n_header-1)
    if not col_list:
        col_list=range(1,len(tmp.dtype.names))
    col_names=tmp.dtype.names

    # now get the remaining column names (how is there not a better way?)
    if (named_struct):
        raw_data=np.genfromtxt(file, delimiter="\t", usecols=col_list,
                               names=True, skip_header=n_header-1)
    else:
        raw_data=np.genfromtxt(file, delimiter="\t", usecols=col_list,
                               skip_header=n_header-1)
        
    return row_names, col_names, raw_data

# Make a numpy array of y-vals for a power law given x-vals
def power_law(x_points, a, B=1):
    # format B*x^a
    y_vals = np.power(x_points, a)
    y_vals = y_vals*B
    return y_vals

# Calculate a histogram that is the ratio of histograms for two sets of data
def frac_hist(spec_ys, tot_ys, bin_size=1):
    tot_hist, z = np.histogram(tot_ys, bin_size)
    spec_hist, z = np.histogram(spec_ys, bin_size)
    frac_hist, z = spec_hist.astype(float)/tot_hist.astype(float)

    return tot_hist, fract_hist

# Calculate the line that best fits the data using weighted least squares
# Assumes the ideal solution is of the form y = A + Bx
# (Input must be numpy arrays)
def ls_fit(xs, ys, ws=None):

    if ws is None:
        n_pts = xs.shape
        weights = np.ones(n_pts,)
    else:
        weights = ws
    
    print "weights ", weights 
    x_sq = weights*np.power(xs,2)
    sum_x_sq = x_sq.sum()
    sum_x = (weights*xs).sum()
    xy = weights*xs*ys
    sum_xy = xy.sum()
    sum_y = (weights*ys).sum()
    sum_w = weights.sum()

    denom = sum_w*sum_x_sq - np.power(sum_x, 2)
    A_num = sum_x_sq*sum_y - sum_x*sum_xy
    B_num = sum_w*sum_xy - sum_x*sum_y

    A = A_num/denom
    B = B_num/denom

    return A, B

    
#def rms_fit_quality(data, model):

