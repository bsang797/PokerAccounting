from tkinter import *
import tkinter.font as font
from tkinter import ttk
from Functions import *
import Reconciliation as rec
from datetime import datetime
from FormGenerator import *

class MainMenu:
    def __init__(self, overview_file, people_file, roles_file, shift_file, transactions_file):
        self.root = Tk()
        self.root.resizable(False, False)
        self.session_id = data_exporter(transactions_file)['session_id'].max() #+ 1

        self.font_style = "Helvetica"
        self.button_fontsize = 10
        self.label_fontsize = 10
        self.bg_color = "#F0F0F0"
        self.root.title("Poker Accounting System")

        self.overview_file = overview_file
        self.people_file = people_file
        self.roles_file = roles_file
        self.shift_file = shift_file
        self.transactions_file = transactions_file

        self.reconciliation_data = rec.Reconciliation(
            data_exporter(self.transactions_file),
            data_exporter(self.shift_file),
            data_exporter(self.people_file))

    def main_tasks(self):
        self.load_chip_data()
        self.load_debt_data()
        self.buttons()
        self.tabs()
        self.chip_labels()
        self.debt_labels()
        self.x = 0
        self.root.mainloop()

    def load_chip_data(self):
        chips_purchased_series = self.reconciliation_data.chips_purchased()
        chips_cashed_series = self.reconciliation_data.chips_cashed()
        chips_float_series = self.reconciliation_data.chips_floating()
        total_rake_series = self.reconciliation_data.total_rake()
        total_tips_series = self.reconciliation_data.total_tips()
        debt_outstanding_series = self.reconciliation_data.debt_outstanding_by_player()

        self.chips_purchased = chips_purchased_series[chips_purchased_series.idxmax()]
        self.chips_cashed = -chips_cashed_series[chips_cashed_series.idxmax()]
        self.chips_float = chips_float_series[chips_float_series.idxmax()]
        self.total_rake = total_rake_series[total_rake_series.idxmax()]
        self.total_tips = total_tips_series[total_tips_series.idxmax()]
        self.total_debt = debt_outstanding_series.agg('sum')

    def load_debt_data(self):
        debt_outstanding_series = self.reconciliation_data.debt_outstanding_by_player()
        debts = pd.merge(data_exporter(self.people_file),
                         debt_outstanding_series,
                         how="inner",
                         on="person_id").drop(["person_id",
                                               "phone_num",
                                               "email",
                                               "address"], axis=1)
        self.debt_byperson = []
        j = 0
        for i in debts.iterrows():
            if i[1]["quantity"] != 0:
                self.debt_byperson.append([])
                name = i[1]["first_name"] + " " + i[1]["last_name"]
                self.debt_byperson[j] = [name, str(i[1]["quantity"])]
                j += 1
        self.debt_byperson.sort(key=lambda x: x[0])

    def buttons(self):
        buying_in_button = Button(self.root, width=15, text="Buying In",
                                  command=self.buyin_button)
        cashing_out_button = Button(self.root, width=15, text="Cashing Out")
        debt_button = Button(self.root, width=15, text="Debt Repayment")
        shift_button = Button(self.root, width=15, text="End of Shift")
        report_button = Button(self.root, width=15, text="Create Report")
        quit_button = Button(self.root, width=10, text="Quit")

        self.format_buttons([buying_in_button, cashing_out_button, debt_button,
                             shift_button, report_button, quit_button])

    def format_buttons(self, buttons):
        i = 0
        for button in buttons:
            button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
            button.grid(row=i, column=2)
            i += 1

    def tabs(self):
        self.tab_parent = ttk.Notebook(self.root)
        self.chip_tab = ttk.Frame(self.tab_parent)
        self.debt_tab = ttk.Frame(self.tab_parent)

        self.tab_parent.add(self.chip_tab, text="Overview")
        self.tab_parent.add(self.debt_tab, text="Outstanding Debts")

        self.tab_parent.grid(row=0, column=0, sticky="nw", rowspan=6, columnspan=2)

    def debt_labels(self):
        v = Scrollbar(self.debt_tab)
        v.pack(side=RIGHT, fill=Y)

        t = Text(self.debt_tab, width=0, height=8, wrap=NONE, yscrollcommand=v.set)
        t['font'] = font.Font(family=self.font_style, size=self.button_fontsize)

        for i in self.debt_byperson:
            t.insert(END, i[0] + ": " + i[1] + "\n")
        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)

    def chip_labels(self):
        description = Label(self.chip_tab, text="Description", bg=self.bg_color)
        amount = Label(self.chip_tab, text="Amount", bg=self.bg_color)

        desc_purchased = Label(self.chip_tab, text="Chips Purchased", bg=self.bg_color)
        purchased_amt = Label(self.chip_tab, text=self.chips_purchased, bg=self.bg_color)

        desc_cashed = Label(self.chip_tab, text="Chips Cashed Out", bg=self.bg_color)
        cashed_amt = Label(self.chip_tab, text=self.chips_cashed, bg=self.bg_color)

        desc_float = Label(self.chip_tab, text="Chips Currently in Play", bg=self.bg_color)
        float_amt = Label(self.chip_tab, text=self.chips_float, bg=self.bg_color)

        desc_rake = Label(self.chip_tab, text="Rake Collected", bg=self.bg_color)
        rake_amt = Label(self.chip_tab, text=self.total_rake, bg=self.bg_color)

        desc_tips = Label(self.chip_tab, text="Tips Collected", bg=self.bg_color)
        tips_amt = Label(self.chip_tab, text=self.total_tips, bg=self.bg_color)

        desc_debt = Label(self.chip_tab, text="Total Debt", bg=self.bg_color)
        debt_amt = Label(self.chip_tab, text=self.total_debt, bg=self.bg_color)

        self.format_chip_labels([[description, amount],
                                 [desc_purchased, purchased_amt],
                                 [desc_cashed, cashed_amt],
                                 [desc_float, float_amt],
                                 [desc_rake, rake_amt],
                                 [desc_tips, tips_amt],
                                 [desc_debt, debt_amt]])

    def format_chip_labels(self, labels):
        i = 0
        for pair in labels:
            for label in pair:
                label['font'] = font.Font(family=self.font_style, size=self.label_fontsize)
            pair[0].grid(row=i, column=0, sticky="nw")
            pair[1].grid(row=i, column=1, sticky="nw")
            i += 1

    def buyin_button(self):
        transaction_id = data_exporter(self.transactions_file)['transaction_id'].max() + 1
        date_time = datetime.now()
        chip_purchase = 1

        self.root.quit()
        new_root = Tk()
        new_root.mainloop()