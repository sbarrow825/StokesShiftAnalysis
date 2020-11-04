from Utils import *

class DecayDict:

    def __init__(self, decay_dict, SS_dict):

        self.temps = SS_dict.temps
        self.wavelengths = self.getWavelengths(decay_dict)
        self.wavenumbers = self.getWavenumbers(decay_dict)
        self.data = {}
        for temp in self.temps:
            self.data[temp] = {}
            for wavenumber in self.wavenumbers:
                self.data[temp][wavenumber] = {}
        for colName in list(decay_dict.keys())[1:]:
            if (colName[0] == "t" or colName[0] == "a") and colName[-1].isdigit() and len(colName) == 2:
                col = list(decay_dict[colName].values())
                ColSplit = splitCol(col, colName)
                for thisTempValues, temp in zip(ColSplit, self.temps):
                    for thisWavenumberValue, wavenumber in zip(thisTempValues, self.wavenumbers):
                        self.data[temp][wavenumber][colName] = thisWavenumberValue

    def getWavenumbers(self, decay_dict):
        wavenumbers = []
        for wavelength in list(decay_dict["Wavelength"].values()):
            if wavelength == "Wavelength":
                break
            wavenumbers.append(1/(wavelength*10**(-7)))
        return wavenumbers

    def getWavelengths(self, decay_dict):
        wavelengths = []
        for wavelength in list(decay_dict["Wavelength"].values()):
            if wavelength == "Wavelength":
                break
            wavelengths.append(wavelength)
        return wavelengths
