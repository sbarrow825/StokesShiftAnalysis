from tkinter import *

numbers = []
operations = []

root = Tk()
root.title("Calculator")

def action(button):
    numberToAdd = button['text']
    currentLabel = mainLabel["text"]
    newText = currentLabel + numberToAdd
    mainLabel.config(text=newText)

def calculateNumber():
    mainLabel.config(text = str(eval(mainLabel["text"])))

# def addOne():
#     currentLabel = mainLabel["text"]
#     newLabel = Label(root, text=currentLabel + "1")
#     newLabel.grid(row=0, columnspan=3)
#     print(self)
#     return

# def addTwo():
#     return

# def addThree():
#     return

# def addFour():
#     return

# def addFive():
#     return

# def addSix():
#     return

# def myClick():
#     myLabel = Label(root, text="Hello " + e.get())
#     myLabel.grid(row=2, column=1)

# myLabel1 = Label(root, text="This is dumb")
# myLabel2 = Label(root, text="xd lumfow")

# myLabel1.grid(row=0, column=0)
# myLabel2.grid(row=1, column=0)
mainLabel = Label(root, text="")
mainLabel.grid(row=0, columnspan=3)

one = Button(root, text="1", command=lambda: action(one))
one.grid(row=1, column=0)
two = Button(root, text="2", command=lambda: action(two))
two.grid(row=1, column=1)
three = Button(root, text="3", command=lambda: action(three))
three.grid(row=1, column=2)
four = Button(root, text="4", command=lambda: action(four))
four.grid(row=2, column=0)
five = Button(root, text="5", command=lambda: action(five))
five.grid(row=2, column=1)
six= Button(root, text="6", command=lambda: action(six))
six.grid(row=2, column=2)
add = Button(root, text="+", command=lambda: action(add))
add.grid(row=3, column=0)
subtract = Button(root, text="-", command=lambda: action(subtract))
subtract.grid(row=3, column=1)
multiply = Button(root, text="*", command=lambda: action(multiply))
multiply.grid(row=3, column=2)
calculate = Button(root, text="=", command=calculateNumber)
calculate.grid(row=4, columnspan=3)

root.mainloop()