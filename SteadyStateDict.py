from Utils import *

class SteadyStateDict:

    def __init__(self, SS_dict):

        self.temps = list(SS_dict.keys())[1:]
        self.wavelengths = list(SS_dict["Wavelength"].values())
        self.wavenumbers = [1/(wavelength*10**(-7)) for wavelength in self.wavelengths]
        self.data = {}
        for temp in self.temps:
            self.data[temp] = {}
            lambdaMax = max(list(SS_dict[temp].values()))
            for wavenumber, value in zip(self.wavenumbers, list(SS_dict[temp].values())):
                self.data[temp][wavenumber] = value / lambdaMax