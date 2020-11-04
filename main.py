import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
from Utils import *

SS_df = pd.read_excel("steadyStateData.xlsx")
decay_df = pd.read_excel("decayData.xlsx")

SS_df_dict = SS_df.to_dict()
SS_df_dict_organized = organizeSSDict(SS_df_dict)

decay_df_dict = decay_df.to_dict()
decay_df_dict_organized = organizeDecayDict(decay_df_dict, SS_df_dict_organized)

FI_dict = getFluorescenceIntensityDict(SS_df_dict_organized, decay_df_dict_organized)

VP_dict = conductLogNormalFits(FI_dict)

graphNormalizedTRES(VP_dict)

CT_dict = graphNormalizedCT(VP_dict)

EA_dict = fitTwoExpDecays(CT_dict)

final_dict = calculateEAs(EA_dict)

plt.tight_layout()
plt.show()