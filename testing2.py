from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog

root = Tk()

def findSteadyStateData():
    SS_filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel Files","*.xlsx"), ("all files", "*.*")))
    Label(root, text=SS_filename).pack()

steadyStateButton = Button(root, text="Select Steady State Data", command=findSteadyStateData).pack()

# progress = Progressbar(root, orient = HORIZONTAL, length = 100, mode = 'determinate')

# def bar():
#     import time
#     for i in range(100000):
#         progress["value"] = i/1000
#         root.update_idletasks()

# progress.pack(pady=10)

# Button(root, text = 'Start', command = bar).pack(pady = 10)

root.mainloop()