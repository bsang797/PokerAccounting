import csv
from datetime import datetime
import os
import FormGenerator as FG

file = os.getcwd()+"/Data/buy_in_transactions.csv"
form_name = os.path.splitext(os.path.basename(file))[0]

with open(file, "r") as f:
    reader = csv.reader(f)
    form_fields = next(reader)

def append_list_as_row(file_name, list_of_elem):
    if list_of_elem == []:
        quit()
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(list_of_elem)

append_list_as_row(file, FG.FormGenerator(form_name,form_fields).run())