import numpy as np
import pandas as pd
from tkinter import *
from tkinter import messagebox
from scipy.optimize import curve_fit, least_squares
from scipy.stats import chisquare, linregress
import matplotlib.pyplot as plt

def organizeSSDict(SSdict):
    # restructures the steady state dictionary and normalizes the max intesity at each temp to 1
    # organizedSSdict takes the structure of organizedSSdict[temp][wavenumber] = double between 0 and 1
    # also have organizedSSdict["Wavelength"] = all measured wavelengths
    # also have organizedSSdict["Wavenumber"] = all measured wavenumbers (same as wavelength but converted)
    organizedSSdict = {}
    organizedSSdict["Wavelength"] = list(SSdict["Wavelength"].values())
    organizedSSdict["Wavenumber"] = getListOfWavenumbers(list(SSdict["Wavelength"].values()))
    for temp in list(SSdict.keys())[1:]: 
        lambdaMax = max(list(SSdict[temp].values()))
        organizedSSdict[temp] = {}
        for wavenumber, index in zip(organizedSSdict["Wavenumber"], list(SSdict[temp].keys())):
            organizedSSdict[temp][wavenumber] = SSdict[temp][index] / lambdaMax
    return organizedSSdict

def organizeDecayDict(decayDict, organizedSSdict):
    # Organizes the decay data such that
    # organizedDecayDict[temp][wavenumber]["a"]["a1"] = alpha 1 value
    # organizedDecayDict[temp][wavenumber]["t"]["t1"] = tau 1 value
    organizedDecayDict = {}
    for temp in list(organizedSSdict.keys())[2:]:
        organizedDecayDict[temp] = {}
        for wavelength in organizedSSdict["Wavelength"]:
            wavenumber = wavelengthToWavenumber(wavelength)
            organizedDecayDict[temp][wavenumber] = {"a": {}, "t": {}}
    columns = list(decayDict.keys())
    for name in columns:
        if (name[0] == 't' or name[0] == "a") and name[-1].isdigit() and len(name) == 2:
            Col = list(decayDict[name].values())
            ColSplit = splitCol(Col, name)
            for thisTempValues, temp in zip(ColSplit, list(organizedSSdict.keys())[2:]):
                for thisWavenumberValue, wavenumber in zip(thisTempValues, organizedSSdict["Wavenumber"]):
                    organizedDecayDict[temp][wavenumber][name[0]][name] = thisWavenumberValue
    return organizedDecayDict

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

# def getFluorescenceIntensityDict(SSDict, decayDict, trange=np.linspace(0, tUpperLimit, 1001, endpoint=True)):
#     # FI_dict[temp][time][wavenumber] = FI_value
#     FI_dict = {}
#     for temp in list(decayDict.keys()):
#         FI_dict[temp] = {}
#         for time in trange:
#             time = round(time, 2)
#             FI_dict[temp][time] = {}
#             for wavenumber in SSDict["Wavenumber"]:
#                 F = SSDict[temp][wavenumber]
#                 alphas = list(decayDict[temp][wavenumber]["a"].values())
#                 taus = list(decayDict[temp][wavenumber]["t"].values())
#                 FI_dict[temp][time][wavenumber] = computeFI(F, alphas, taus, time)
#     return FI_dict

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

def getListOfWavenumbers(wavelengthList):
    return [wavelengthToWavenumber(wavelength) for wavelength in wavelengthList]

def wavelengthToWavenumber(wavelength):
    return 1/(wavelength*10**(-7))

def curveFunc(x, h, gamma, vp, delta):
    return h * np.exp(-np.log(2)*((np.log(1+(2*gamma*(x-vp)/delta)))/gamma)**2)

def conductLogNormalFits(FI_dict):
    curveFitCount = 0
    curveFitsNeeded = len(list(FI_dict.keys())) * 1001
    for temp in list(FI_dict.keys()):
        for time in np.linspace(0, tUpperLimit, 1001, endpoint=True):
            time = round(time, 2)
            xData = list(FI_dict[temp][time].keys())[:-1]
            yData = list(FI_dict[temp][time].values())[:-1]
            popt, pcov = curve_fit(curveFunc, xData, yData, bounds=((0, 0, min(xData), 0), (100, 1, max(xData), 10000)))
            FI_dict[temp][time]["vp"] = popt[-2]
            curveFitCount += 1
            if curveFitCount % 100 == 0:
                print("completed {0} out of {1} curve fits".format(curveFitCount, curveFitsNeeded))
    return FI_dict

def graphNormalizedTRES(VP_dict):
    for temp, index in zip(list(VP_dict.keys()), range(len(list(VP_dict.keys())))):
        plt.figure(index)
        tempDict = VP_dict[temp]
        for time in np.linspace(0, tUpperLimit, 11, endpoint=True):
            time = round(time, 2)
            xData = list(tempDict[time].keys())[:-1]
            yData = list(tempDict[time].values())[:-1]
            popt, pcov = curve_fit(curveFunc, xData, yData, bounds=((0, 0, min(xData), 0), (100, 1, max(xData), 10000)))
            minX = min(xData)
            maxX = max(xData)
            xModelData = np.linspace(minX, maxX, 100)
            yModelData = []
            for data in xModelData:
                yModelData.append(curveFunc(data, *popt))
            maxIntensity = max(yModelData)
            yModelData = [data / maxIntensity for data in yModelData]
            plt.plot(xModelData, yModelData, label=str(time) + " ns")
        plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
        plt.title(str(temp) + " deg C normalized TRES")
        plt.xlabel('Wavenumber (cm^-1)')

def graphNormalizedCT(VP_dict):
    plt.figure(100)
    for temp in list(VP_dict.keys()):
        xData = list(VP_dict[temp].keys())
        SSPeakEmissionMaxima = VP_dict[temp][list(VP_dict[temp].keys())[-1]]["vp"]
        yData = []
        for time in list(VP_dict[temp].keys()):
            if not time:
                VP_dict[temp][time]["ct"] = 1
                t0PeakEmissionMaxima = VP_dict[temp][time]["vp"]
            elif time == list(VP_dict[temp].keys())[-1]:
                VP_dict[temp][time]["ct"] = 0
            else:
                VP_dict[temp][time]["ct"] = (VP_dict[temp][time]["vp"] - SSPeakEmissionMaxima)/(t0PeakEmissionMaxima - SSPeakEmissionMaxima)
            yData.append(VP_dict[temp][time]["ct"])
        plt.scatter(list(filter(lambda x : xData.index(x) % 10 == 0, xData)), list(filter(lambda y : yData.index(y) % 10 == 0, yData)), label=str(temp) + " deg C")
    return VP_dict

def twoExpDecay(t, alpha, tau1, tau2):
    return alpha*np.exp(-t/tau1) + (1 - alpha)*np.exp(-t/tau2)

def fitTwoExpDecays(CT_dict):
    for temp in list(CT_dict.keys()):  
        xData = list(CT_dict[temp].keys())
        yData = [CT_dict[temp][time]["ct"] for time in xData]
        popt, pcov = curve_fit(twoExpDecay, xData, yData, p0=[0.5, 0.5, 5], bounds=((0, 0, 0), (1, 100, 100)))
        print("tau 1 is " + str(popt[1]) + " at temperature " + str(temp))
        print("tau 2 is " + str(popt[2]) + " at temperature " + str(temp))
        xModelData = xData
        yModelData = [twoExpDecay(t, *popt) for t in xModelData]
        CT_dict[temp]["t1"] = popt[1]
        CT_dict[temp]["t2"] = popt[2]
        chiSquared = chisquare(yData, f_exp=yModelData)[0]
        plt.plot(xModelData, yModelData, label=str(temp) + " deg C, tUpper = " + str(tUpperLimit) + 'ns, chi^2 = ' + str(chiSquared))
    plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
    plt.title("Temperature Dependent Stokes Shift Decays")
    plt.xlabel('Time (ns)')
    return CT_dict

def calculateEAs(EA_dict):
    plt.figure(200)
    xData = [1000/(temp + 273.15) for temp in list(EA_dict.keys())]
    y1Data = [np.log(1/(EA_dict[temp]["t1"])) for temp in list(EA_dict.keys())]
    y2Data = [np.log(1/(EA_dict[temp]["t2"])) for temp in list(EA_dict.keys())]
    plt.scatter(xData, y1Data, label="tau 1")
    plt.scatter(xData, y2Data, label="tau 2")
    slope1, intercept1, r_value1, p_value1, std_err1 = linregress(xData, y1Data)
    slope2, intercept2, r_value2, p_value2, std_err2 = linregress(xData, y2Data)
    y1ModelData = [slope1*invK + intercept1 for invK in xData]
    y2ModelData = [slope2*invK + intercept2 for invK in xData]
    plt.plot(xData, y1ModelData, label="tau 1 linear fit, slope = {0}, r^2 = {1}".format(round(slope1, 2), round(r_value1 ** 2, 2)))
    plt.plot(xData, y2ModelData, label="tau 2 linear fit, slope = {0} r^2 = {1}".format(round(slope2, 2), round(r_value2 ** 2, 2)))
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.title("Arrhenius Plot Linear Regression")
    plt.xlabel('Temperature (1/K)')
    plt.ylabel("ln(1/tau)")
    print("slope 1: " + str(slope1))
    print("slope 2: " + str(slope2))