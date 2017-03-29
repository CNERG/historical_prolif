#! /usr/bin/env python

import math
import numpy as np
import sys
import io



# Return the mean values of a 1-D array
def mean(l_Z):
    Z_tot = 0
    N = len(l_Z)
    for i in range(N):
        Z_tot += l_Z[i] / N
    return Z_tot

# Compute the Covariance between X and Y
def Cov_XY(X,Y):
    XY_tot = 0
    if  len(X) != len(Y):
        return NAN
    else:
        X_mean = mean(X)
        Y_mean = mean(Y)
        N = len(X)
        for i in range(N):
            XY_tot += (X[i] - X_mean)*(Y[i]-Y_mean)/N
    return XY_tot

# Compute the Standart Deviation of Z
def s_Z(Z):
    Z_tot = 0
    Z_mean = mean(Z)
    N = len(Z)
    for i in range(N):
        Z_tot += (Z[i] - Z_mean)*(Z[i] - Z_mean)/N
    return math.sqrt(Z_tot)

# Compute the correlation factor between 2 1-D array
def Cor_XY(X,Y):
    c_XY = Cov_XY(X,Y) / ( s_Z(X) * s_Z(Y) )
    return c_XY

def Cor_matrix(data):
    data_dim = data.shape
    M_cor = np.matrix( np.zeros((data_dim[1],data_dim[1])) )
    for u in range(data_dim[1]):
        for v in range(data_dim[1]):
            M_cor[u,v] = Cor_XY(data[:,u],data[:,v])
    np.set_printoptions(precision=2,linewidth=100)
    return M_cor

def Compute_Score(w, f):
    s = 0.
    if len(w) != len(f):
        return NAN
    else:
        for i in range(len(w)):
            s+= w[i]*f[i]
    return s


def main():
    data_file = open(sys.argv[1], 'r')
    Cor_matrix(np.loadtxt(data_file))



if __name__ == "__main__":
    main()
