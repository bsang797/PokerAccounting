import pandas as pd
import os
import csv

def data_exporter(file_directory):
    return pd.read_csv(file_directory)

def append_list_as_row(file_name, list_of_elem):
    if list_of_elem == []:
        quit()
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(list_of_elem)