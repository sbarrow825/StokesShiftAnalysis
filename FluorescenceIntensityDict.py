import numpy as np
from tkinter import *
from scipy.optimize import curve_fit, least_squares
from scipy.stats import chisquare, linregress
import matplotlib.pyplot as plt
from Utils import *

class FluorescenceIntensityDict:

    def __init__(self, SS_dict, decay_dict, trange, tUpperLimit, includeTRES, includeCT, root):
        self.root = root
        self.tUpperLimit = tUpperLimit
        self.includeTRES = includeTRES
        self.includeCT = includeCT
        self.temps = decay_dict.temps
        self.wavenumbers = decay_dict.wavenumbers
        self.wavelengths = decay_dict.wavelengths
        self.data = {}
        for temp in list(decay_dict.data.keys()):
            self.data[temp] = {}
            for time in trange:
                self.data[temp][time] = {}
                for wavenumber in decay_dict.wavenumbers:
                    F = SS_dict.data[temp][wavenumber]
                    alphas = self.getAlphas(decay_dict, temp, wavenumber)
                    taus = self.getTaus(decay_dict, temp, wavenumber)
                    self.data[temp][time][wavenumber] = computeFI(F, alphas, taus, time)

    def getAlphas(self, decay_dict, temp, wavenumber):
        alphas = []
        for name in list(decay_dict.data[temp][wavenumber].keys()):
            if name[0] == "a":
                alphas.append(decay_dict.data[temp][wavenumber][name])
        return alphas

    def getTaus(self, decay_dict, temp, wavenumber):
        taus = []
        for name in list(decay_dict.data[temp][wavenumber].keys()):
            if name[0] == "t":
                taus.append(decay_dict.data[temp][wavenumber][name])
        return taus

    def conductLogNormalFits(self, trange, root):
        curveFitCount = 0
        curveFitsNeeded = len(trange) * len(self.temps)
        for temp in self.temps:
            prevGuess = False # get rid of the previous guess from the last temperature
            for time in trange:
                xData = list(self.data[temp][time].keys())
                yData = list(self.data[temp][time].values())
                if not prevGuess: # if this is the first curve fit for this temperature
                    popt, pcov = curve_fit(curveFunc, xData, yData, bounds=((0, 0, min(xData), 0), (100, 1, max(xData), 10000))) # curve fit to establish peak emission maxima value (vp)
                else:
                    popt, pcov = curve_fit(curveFunc, xData, yData, p0=prevGuess, bounds=((0, 0, min(xData), 0), (100, 1, max(xData), 10000))) # curve fit to establish peak emission maxima value (vp)
                self.data[temp][time]["vp"] = popt[-2]
                self.data[temp][time]["fitParams"] = [*popt]
                prevGuess = [*popt] # update the inital guess for the next fit to be the results from this fit
                curveFitCount += 1
                if curveFitCount % 100 == 0:
                    print("completed {0} out of {1} curve fits".format(curveFitCount, curveFitsNeeded))
                    Label(root, text="completed {0} out of {1} curve fits".format(curveFitCount, curveFitsNeeded)).grid(row=5, column=1)
                    root.update_idletasks()


    def graphNormalizedTRES(self, trange):
        if not self.includeTRES:
            return
        counter = 0
        plotCounter = 1
        for temp in self.temps: # for each temperature
            plt.figure(plotCounter)
            for time in list(self.data[temp].keys()): # for each time in this temperature
                if not counter % (len(trange) // 5): # plots 10 evenly spaced time points per TRES regardless of trange length
                    xModelData = np.linspace(min(self.wavenumbers), max(self.wavenumbers), 100) # sample 100 evenly spaced points in our wavenumber domain
                    yModelData = [curveFunc(wavenumber, *self.data[temp][time]["fitParams"]) for wavenumber in xModelData]
                    maxIntensity = max(yModelData)
                    yModelDataNormalized = [data / maxIntensity for data in yModelData]
                    plt.plot(xModelData, yModelDataNormalized, label=str(round(time, 2)) + " ns")
                counter += 1
            plotCounter += 1
            plt.legend()
            plt.title(str(temp) + " deg C normalized TRES")
            plt.xlabel('Wavenumber (cm^-1)')
            plt.ylabel('Normalized FI')
  
    def graphNormalizedCT(self, trange):
        if self.includeCT:
            plt.figure(200)
        for temp in self.temps: # for every temperature
            xData, yData = [], [] # reset x and y data to empty lists for each new temperature
            counter = 0
            peakEmmisionMaximaSS = self.data[temp][self.tUpperLimit]["vp"] # vInf = final peak emmision maxima in time range
            for time in list(self.data[temp].keys()): # for each time at this temperature
                if not time:
                    self.data[temp][time]["ct"] = 1 # if time = 0, ct = 1
                    t0PeakEmissionMaxima = self.data[temp][time]["vp"] # vp(t = 0) is this vp value
                elif time == self.tUpperLimit:
                    self.data[temp][time]["ct"] = 0 # if this is the last point, vp = vpSS = vpInf
                else:
                     # if 0 < time > tUpperLimit, vp is give by the equation [vp(t) - vp(t = inf)]/[vp(t = 0) - vp(t = inf)]
                     # note that we're assuming vp(t = tUpperLimit) = vp(t = inf) = vp(t = steady state time)
                    self.data[temp][time]["ct"] = (self.data[temp][time]["vp"] - peakEmmisionMaximaSS)/(t0PeakEmissionMaxima - peakEmmisionMaximaSS)
                if not counter % 100: # is true every 100 loops, avoids plotting too many points on the graph
                    xData.append(time)
                    yData.append(self.data[temp][time]["ct"])
                counter += 1
            if self.includeCT:
                plt.scatter(xData, yData)

    def fitTwoExponentialDecays(self, trange):
        prevGuess = [0.5, 0.5, 5] # start out with hardcoded initial guesses for the curve fit
        for temp in self.temps:
            xData = list(self.data[temp].keys()) # all times at this temperature
            yData = [self.data[temp][time]["ct"] for time in xData] # all ct values at this temperature
            popt, pcov = curve_fit(twoExpDecay, xData, yData, p0=prevGuess, bounds=((0, -np.inf, -np.inf), (1, np.inf, np.inf))) # use the previous curvefit paraments as the initial guess for this fit
            self.data[temp]["tau1"] = popt[1]
            self.data[temp]["tau2"] = popt[2]
            prevGuess = [*popt] # update the initial values for the next fit to be this fit's parameters
            yModelData = [twoExpDecay(time, *popt) for time in xData] # plugging our xData into our curvefit model
            chiSquared = chisquare(yData, f_exp=yModelData)[0] # goodness of fit parameter calculation
            if self.includeCT:
                plt.plot(xData, yModelData, label=str(temp) + " deg C, chi^2 = " + str(round(chiSquared, 2)))
        if self.includeCT:
            plt.legend()
            plt.title("Temperature Dependent Stokes Shift Decays")
            plt.xlabel('Time (ns)')
            plt.ylabel("Normalized c(t)")

    def ArrheniusPlot(self, trange):
        plt.figure(300)
        xData = [1000/(temp + 273.15) for temp in self.temps] # converting deg C into 1000/K
        tau1Data = [np.log(1/self.data[temp]["tau1"]) for temp in self.temps] # converting tau1 to ln(1/tau1)
        tau2Data = [np.log(1/self.data[temp]["tau2"]) for temp in self.temps] # converting tau2 to ln(1/tau2)
        plt.scatter(xData, tau1Data, label="tau 1")
        plt.scatter(xData, tau2Data, label="tau 2")
        tau1Slope, intercept1, r_value1, p_value1, std_err1 = linregress(xData, tau1Data)
        tau2Slope, intercept2, r_value2, p_value2, std_err2 = linregress(xData, tau2Data)
        tau1ModelData = [tau1Slope*x + intercept1 for x in xData]
        tau2ModelData = [tau2Slope*x + intercept2 for x in xData]
        plt.plot(xData, tau1ModelData, label="tau 1 linear fit, slope = {0}, r^2 = {1}".format(round(tau1Slope, 2), round(r_value1 ** 2, 2)))
        plt.plot(xData, tau2ModelData , label="tau 2 linear fit, slope = {0}, r^2 = {1}".format(round(tau2Slope, 2), round(r_value2 ** 2, 2)))
        plt.legend()
        plt.title("Arrhenius Plot Linear Regression")
        plt.xlabel('Temperature (1/K)')
        plt.ylabel("ln(1/tau)")

    def addNoisePositive(self):
        return
        # perturbs all tau values by a random percent change between + 20% of their original value
        for temp in self.temps:
            self.data[temp]["tau1"] += 0.1
            self.data[temp]["tau2"] += 0.1

    def addNoiseNegative(self):
        return
        # perturbs all tau values by a random percent change between - 20% of their original value
        for temp in self.temps:
            self.data[temp]["tau1"] -= 0.1
            self.data[temp]["tau2"] -= 0.1