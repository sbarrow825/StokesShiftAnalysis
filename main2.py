import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from Utils import *
from SteadyStateDict import *
from DecayDict import *
from FluorescenceIntensityDict import *
# from main3 import *

def runReplicate(FI_dict, trange):

    FI_dict.conductLogNormalFits(trange)
    FI_dict.graphNormalizedTRES(trange)
    FI_dict.graphNormalizedCT(trange)
    FI_dict.fitTwoExponentialDecays(trange)
    # FI_dict.ArrheniusPlot(trange)

    return FI_dict