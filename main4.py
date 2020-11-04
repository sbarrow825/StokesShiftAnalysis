from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from main3 import runAnalysis

root = Tk()
root.title("Stokes Shift Analysis")

def findSteadyStateData(steadyStateButton):
    SS_filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel Files","*.xlsx"), ("all files", "*.*")))
    steadyStateButton.config(text=SS_filename)    

def findDecayData(decayButton):
    decay_filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel Files","*.xlsx"), ("all files", "*.*")))
    decayButton.config(text=decay_filename)

steadyStateButton = Button(root, text="Select Steady State Data", command=lambda: findSteadyStateData(steadyStateButton))
steadyStateButton.pack()
decayButton = Button(root, text="Select Decay Data", command=lambda: findDecayData(decayButton))
decayButton.pack()

def run(steadyStateButton, decayButton, tUpperLimit, includeTRES, includeCT):
    runAnalysis(steadyStateButton["text"], decayButton["text"], tUpperLimit, includeTRES, includeCT)

includeTRES =IntVar()
includeTRESbutton = Checkbutton(root, text="Include TRES plots", var=includeTRES)
includeTRESbutton.pack()

includeCT = IntVar()
includeCTbutton = Checkbutton(root, text="Include normalized c(t) plot", var=includeCT)
includeCTbutton.pack()

tUpperLimit = 5

runButton = Button(root, text="Run", command=lambda: run(steadyStateButton, decayButton, tUpperLimit, includeTRES, includeCT))
runButton.pack()

root.mainloop()