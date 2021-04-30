import tkinter as tk
import tksheet
import pandas as pd
import os

df = pd.read_csv(os.getcwd()+"/Data/transactions.csv")
top = tk.Tk()
sheet = tksheet.Sheet(top)
sheet.grid()
sheet.set_sheet_data(df.values.tolist())
# table enable choices listed below:
top.mainloop()