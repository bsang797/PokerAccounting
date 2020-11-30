from tkinter import *

root = Tk()
Button(root, text = "Brighten").grid(row=2, column=0)
Button(root, text = "Darken").grid(row=3, column=0)
Button(root, text = "Warm").grid(row=4, column=0)
Button(root, text = "Cool").grid(row=5, column=0)
root.mainloop()