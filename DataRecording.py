import os
import FormGenerator as FG
from Functions import *

file = os.getcwd()+"/Data/transactions.csv"
form_name = os.path.splitext(os.path.basename(file))[0]

with open(file, "r") as f:
    reader = csv.reader(f)
    form_fields = next(reader)

append_list_as_row(file, FG.FormGenerator(form_name,form_fields).run())