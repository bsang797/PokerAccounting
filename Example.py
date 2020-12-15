import pandas
import webbrowser
import os
from Functions import *
import Reconciliation as rec
from MainMenu import *
from datetime import datetime

overview_file = os.getcwd()+"/Data/overview.csv"
people_file = os.getcwd()+"/Data/people.csv"
roles_file = os.getcwd()+"/Data/roles.csv"
shift_file = os.getcwd()+"/Data/shift.csv"
transactions_file = os.getcwd()+"/Data/transactions.csv"

# === EOD Reconciliation HTML
def eodrec():
    chips_purchased = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).chips_purchased()
    chips_cashed = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).chips_cashed()
    debt_outstanding = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).debt_outstanding_by_player()
    total_rake = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).total_rake()
    total_tips = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).total_tips()
    chips_float = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).chips_floating()

    print(chips_purchased.idmax)

    html_table = [["header", "End of Day Reconciliation"],
                  ["chips purchased", str(chips_purchased[1])],
                  ["chips cashed", str(chips_cashed[1])],
                  ["chips out on the tables", str(chips_float[1])],
                  ["debt outstanding", str(debt_outstanding.agg("sum"))],
                  ["total rake", str(total_rake[1])],
                  ["total tips", str(total_tips[1])]]

    webbrowser.open(html_temp_file_generator(html_table))

# === Debts per person HTML

def debts_byppl():
    debt_outstanding = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).debt_outstanding_by_player()
    debts = pd.merge(data_exporter(people_file),
                   debt_outstanding,
                   how="inner",
                   on="person_id").drop(["person_id",
                                         "phone_num",
                                         "email",
                                         "address"], axis=1)

    debt_byperson = [["header", "Debts per Person"]]
    j = 1
    for i in debts.iterrows():
        debt_byperson.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        debt_byperson[j] = [name, str(i[1]["quantity"])]
        j += 1
    webbrowser.open(html_temp_file_generator(debt_byperson))

# === Main Menu

MainMenu(overview_file, people_file, roles_file, shift_file, transactions_file).main_tasks()
# print(datetime.now())

# FormGenerator("Buying In Transaction", ['person', 'transaction_type', 'quantity', 'email recipient']).run()
#
# root = Tk()
#
# lab = Label(root)
# lab.pack()
#
# def clock():
#     time = datetime.now().strftime("Time: %H:%M:%S")
#     lab.config(text=time)
#     #lab['text'] = time
#     root.after(1000, clock) # run itself again after 1000 ms
#     root.mainloop()
#
#
# # run first time
# clock()

