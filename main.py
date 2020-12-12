from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
from Utils import *
from SteadyStateDict import *
from DecayDict import *
from FluorescenceIntensityDict import *

root = Tk()
root.title("Stokes Shift Analysis")
root.geometry("800x500")

def runReplicate(FI_dict, trange, root):

    FI_dict.conductLogNormalFits(trange, root)
    FI_dict.graphNormalizedTRES(trange)
    FI_dict.graphNormalizedCT(trange)
    FI_dict.fitTwoExponentialDecays(trange)

    return FI_dict

def findSteadyStateData(steadyStateFilename):
    SS_filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel Files","*.xlsx"), ("all files", "*.*")))
    steadyStateFilename.config(text=SS_filename)    

def findDecayData(decayFilename):
    decay_filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel Files","*.xlsx"), ("all files", "*.*")))
    decayFilename.config(text=decay_filename)

def runAnalysis(SS_pathname, decay_pathname, tUpperLimit, includeTRES, includeCT, root):

    trange = np.linspace(0, tUpperLimit, 1001, endpoint=True)

    SS_df = pd.read_excel(SS_pathname)

    replicates = list(SS_df.to_dict()["Wavelength"].values()).count('Wavelength') # counts how many replicates are in the given data

    replicateConfirmation = messagebox.askyesnocancel(message="Detected data with {0} replicates, is this correct?".format(replicates))

    if not replicateConfirmation:
        sys.exit("Incorrect number of replicates detected, exiting program")

    print("detected data with {0} replicates".format(replicates))

    wavelengthCount = len(splitCol(list(SS_df.to_dict()["Wavelength"].values()), "Wavelength")[0]) # counts how many wavelengths are in the given data

    wavelengthConfirmation = messagebox.askyesnocancel(message="Detected data at {0} different wavelengths, is this correct?".format(wavelengthCount))

    if not wavelengthConfirmation:
            sys.exit("Incorrect number of wavelengths detected, exiting program")

    print("detected data at {0} different wavelengths".format(wavelengthCount))

    SSstart = 0
    SSstop = wavelengthCount

    decay_df = pd.read_excel(decay_pathname)

    temperatureCount = int(((len(decay_df) + 1)/(replicates + 1))/(wavelengthCount + 1))

    temperatureConfirmation = messagebox.askyesnocancel(message="Detected data at {0} different temperatures, is this correct?".format(temperatureCount))

    if not temperatureConfirmation:
        sys.exit("Incorrect number of temperatures detected, exiting program")

    print("detected data at {0} different temperatures".format(temperatureCount))

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

    for replicate_SS_df, replicate_decay_df, index in zip(SS_df_list, decay_df_list, range(len(SS_df_list))):
        replicate_SS_dict = SteadyStateDict(replicate_SS_df.to_dict())
        replicate_decay_dict = DecayDict(replicate_decay_df.to_dict(), replicate_SS_dict)
        replicate_FI_dict = FluorescenceIntensityDict(replicate_SS_dict, replicate_decay_dict, trange, tUpperLimit, includeTRES, includeCT, root)
        finalList.append(runReplicate(replicate_FI_dict, trange, root))

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

steadyStateButton = Button(root, text="Select Steady State Data", command=lambda: findSteadyStateData(steadyStateFilename))
steadyStateButton.grid(row=0, column=0)

steadyStateFilename = Label(root, text="None selected")
steadyStateFilename.grid(row=0, column=1, columnspan=2)

decayButton = Button(root, text="Select Decay Data", command=lambda: findDecayData(decayFilename))
decayButton.grid(row=1, column=0)

decayFilename = Label(root, text="None selected")
decayFilename.grid(row=1, column=1, columnspan=2)

# def run(steadyStateButton, decayButton, tUpperLimit, includeTRES, includeCT):
#     runAnalysis(steadyStateButton["text"], decayButton["text"], tUpperLimit, includeTRES, includeCT)

includeTRES = IntVar()
includeTRESbutton = Checkbutton(root, text="Include TRES plots", var=includeTRES)
includeTRESbutton.grid(row=2, column=0)

includeCT = IntVar()
includeCTbutton = Checkbutton(root, text="Include normalized c(t) plot", var=includeCT)
includeCTbutton.grid(row=3, column=0)

upperLimitEntryLabel = Label(root, text="Time upper limit (ns)")
upperLimitEntry = Entry(root)
tUpperLimit = 5

runButton = Button(root, text="Run", command=lambda: runAnalysis(steadyStateFilename["text"], decayFilename["text"], tUpperLimit, includeTRES, includeCT, root))
runButton.grid(row=4, column=0)

root.mainloop()