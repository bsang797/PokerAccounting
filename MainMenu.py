from tkinter import *
import tkinter.font as font
from datetime import *

class MainMenu:
    def __init__(self):
        self.root = Tk()
        self.font_style = "Helvetica"
        self.header_fontsize = 20
        self.button_fontsize = 15
        self.bg_color = "#F0F0F0"
        self.root.title("Poker Accounting System")

    def mainloop(self):
        self.frames()
        self.placeframes()
        self.buttons()
        self.root.mainloop()

    def frames(self):
        self.graph_frame = Frame(height=500, width=500, bg=self.bg_color, \
                                 highlightbackground="black", highlightcolor="black", highlightthickness=3)
        self.button_frame = Frame(height=500, width=300, bg=self.bg_color)

    def placeframes(self):
        self.graph_frame.grid(row=0, column=0, rowspan=6)
        self.button_frame.grid(row=0, column=1, rowspan=6)

    def buttons(self):
        buying_in_button = Button(self.root, height=2, width=25, text="Buying In")
        buying_in_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        buying_in_button.grid(row=0, column=1)

        cashing_out_button = Button(self.root, height=2, width=25, text="Cashing Out")
        cashing_out_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        cashing_out_button.grid(row=1, column=1)

        debt_button = Button(self.root, height=2, width=25, text="Debt Repayment")
        debt_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        debt_button.grid(row=2, column=1)

        shift_button = Button(self.root, height=2, width=25, text="End of Shift")
        shift_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        shift_button.grid(row=3, column=1)

        report_button = Button(self.root, height=2, width=25, text="Create Report")
        report_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        report_button.grid(row=4, column=1)

        quit_button = Button(self.root, height=1, width=10, text="Quit")
        quit_button['font'] = font.Font(family=self.font_style, size=10)
        quit_button.grid(row=5, column=1)

MainMenu().mainloop()