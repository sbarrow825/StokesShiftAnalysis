import numpy as np
import pandas as pd
from tkinter import *
from tkinter import messagebox
from scipy.optimize import curve_fit, least_squares
from scipy.stats import chisquare, linregress
import matplotlib.pyplot as plt

def splitCol(col, name):
    splitCols = []
    currentCol = []
    for value in col:
        if value == name:
            splitCols.append(currentCol)
            currentCol = []
        else:
            currentCol.append(value)
    splitCols.append(currentCol)
    return splitCols

def computeFI(F, alphas, taus, time):
    return 100*F/sumAlphaTauProducts(alphas, taus)*sumAlphaTauExpProducts(alphas, taus, time)

def sumAlphaTauProducts(alphas, taus):
    res = 0
    for alpha, tau in zip(alphas, taus):
        res += alpha * tau
    return res

def sumAlphaTauExpProducts(alphas, taus, time):
    res = 0
    for alpha, tau in zip(alphas, taus):
        res += alpha * np.exp(-time/tau)
    return res

def curveFunc(x, h, gamma, vp, delta):
    return h * np.exp(-np.log(2)*((np.log(1+(2*gamma*(x-vp)/delta)))/gamma)**2)

def twoExpDecay(t, alpha, tau1, tau2):
    return alpha*np.exp(-t/tau1) + (1 - alpha)*np.exp(-t/tau2)