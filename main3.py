import matplotlib.pyplot as plt
from Utils import *
from main2 import *

def runAnalysis(SS_pathname, decay_pathname, tUpperLimit, includeTRES, includeCT):

    trange = np.linspace(0, tUpperLimit, 1001, endpoint=True)

    SS_df = pd.read_excel(SS_pathname)

    replicates = list(SS_df.to_dict()["Wavelength"].values()).count('Wavelength') # counts how many replicates are in the given data

    print("detected data with {0} replicates".format(replicates))

    wavelengthCount = len(splitCol(list(SS_df.to_dict()["Wavelength"].values()), "Wavelength")[0]) # counts how many wavelengths are in the given data

    print("detected data with {0} different wavelengths".format(wavelengthCount))

    SSstart = 0
    SSstop = wavelengthCount

    decay_df = pd.read_excel(decay_pathname)

    temperatureCount = int(((len(decay_df) + 1)/(replicates + 1))/(wavelengthCount + 1))

    print("detected data with {0} different temperatures".format(temperatureCount))

    decayStart = 0
    decayStop = int((len(decay_df) - replicates)/(replicates + 1))

    SS_df_list = []
    decay_df_list = []

    for i in list(range(replicates + 1)): # loop once for each set of data
        SS_df_list.append(SS_df.iloc[SSstart:SSstop])
        decay_df_list.append(decay_df.iloc[decayStart:decayStop])
        SSstart = SSstop + 1
        SSstop = SSstart + wavelengthCount
        decayStart = decayStop + 1
        decayStop = decayStart + int((len(decay_df) - replicates)/(replicates + 1))

    finalList = []

    for replicate_SS_df, replicate_decay_df in zip(SS_df_list, decay_df_list):
        replicate_SS_dict = SteadyStateDict(replicate_SS_df.to_dict())
        replicate_decay_dict = DecayDict(replicate_decay_df.to_dict(), replicate_SS_dict)
        replicate_FI_dict = FluorescenceIntensityDict(replicate_SS_dict, replicate_decay_dict, trange, tUpperLimit, includeTRES, includeCT)
        finalList.append(runReplicate(replicate_FI_dict, trange))

    # adding artificial noise to tau values. REMOVE THIS LATER!
    finalList[1].addNoisePositive()
    finalList[2].addNoiseNegative()

    plt.figure(300)

    for temp in finalList[0].temps:
        tau1Values = []
        tau2Values = []
        for FI_dict in finalList:
            tau1Values.append(np.log(1/FI_dict.data[temp]["tau1"]))
            tau2Values.append(np.log(1/FI_dict.data[temp]["tau2"]))
        finalList[0].data[temp]["tau1avg"] = np.average(tau1Values)
        finalList[0].data[temp]["tau2avg"] = np.average(tau2Values)
        finalList[0].data[temp]["tau1std"] = np.std(tau1Values)
        finalList[0].data[temp]["tau2std"] = np.std(tau2Values)



    xData = [1000/(temp + 273.15) for temp in finalList[0].temps] # converting deg C into 1000/K
    tau1Data = [finalList[0].data[temp]["tau1avg"] for temp in finalList[0].temps] # converting tau1 to ln(1/tau1)
    # tau1Err = [np.log(1/finalList[0].data[temp]["tau1std"]) for temp in finalList[0].temps] # std for tau1
    tau2Data = [1/finalList[0].data[temp]["tau2avg"] for temp in finalList[0].temps] # converting tau2 to ln(1/tau2)
    # tau2Err = [np.log(1/finalList[0].data[temp]["tau2std"]) for temp in finalList[0].temps] # std for tau2
    plt.scatter(xData, tau1Data, label="tau 1")
    plt.errorbar(xData, tau1Data, yerr=[finalList[0].data[temp]["tau1std"] for temp in finalList[0].temps], ls="none", capsize=5)
    plt.scatter(xData, tau2Data, label="tau 2")
    plt.errorbar(xData, tau2Data, yerr=[finalList[0].data[temp]["tau2std"] for temp in finalList[0].temps], ls="none", capsize=5)
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

    plt.show()