from tkinter import *
from tkinter import ttk
import tkinter.font as font
from Functions import *
from Reports import Reconciliation as rec
from Reports import FinancialReport as fin
from Reports import DealerReport as deal
from Reports import PlayerReport as pplreport
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime
from tkinter import simpledialog
import tksheet

class MainMenu:
    def __init__(self, overview_file, people_file, roles_file, shift_file, transactions_file):


        self.overview_file = overview_file
        self.people_file = people_file
        self.roles_file = roles_file
        self.shift_file = shift_file
        self.transactions_file = transactions_file

        # Define the root
        self.root = Tk()
        self.root.resizable(False, False)
        self.width = 1280
        self.height = 720
        self.session_id = data_exporter(transactions_file)['session_id'].max() + 1
        self.date = datetime.today().strftime('%m-%d-%Y')

        self.font_style = "Helvetica"
        self.button_fontsize = 10
        self.label_fontsize = 10
        self.option_menu_width = 15
        self.bg_color = "#F0F0F0"



        # append_list_as_row(self.overview_file, [self.session_id,
        #                                         self.date,
        #                                         0,
        #                                         120000,
        #                                         35000,
        #                                         0,0,0,0,0])

        #self.root.geometry("128x720")
        self.root.update()

    def mainloop(self):
        self.main_menu()
        self.root.mainloop()

    def main_menu(self):
        self.load_overview_data()
        self.load_ppl_data()
        self.load_chip_data()
        self.load_debt_data()
        self.load_dealer_data()
        self.setup_frames()
        self.sidebar_buttons()
        self.tabs()
        self.debt_labels()
        self.overview_labels()
        self.transact_labels()
        self.fin_tabs()
        self.dealer_tabs()
        self.player_tabs()
        self.rev_tab()
        self.chips_purchaseredemption_tab()
        self.debtsovertime_tab()
        self.rake_overtime_tab()
        self.tips_overtime_tab()
        self.player_overview_tab()
        self.player_debt_tab()
        self.root.title("Poker Accounting System")

    def load_overview_data(self):
        fin_data = fin(data_exporter(self.overview_file),
                       data_exporter(self.transactions_file),
                       data_exporter(self.roles_file),
                       data_exporter(self.shift_file))
        self.overview_rake, self.overview_tips = fin_data.total_revenue()

    def load_ppl_data(self):
        ppl = data_exporter(self.people_file)[['person_id', 'first_name', 'last_name']]
        role = data_exporter(self.roles_file)
        ppl_roles = pd.merge(ppl, role, how="inner", on="person_id")

        self.owners = []
        self.dealers = []
        self.players = []
        self.ppl_id = pd.DataFrame(columns=["person_id", "name"])

        for i in ppl_roles.iterrows():
            if i[1]['role'] == 'Player':
                self.players.append(i[1]['first_name'] + " " + i[1]['last_name'])
            if i[1]['role'] == 'Owner':
                self.owners.append(i[1]['first_name'] + " " + i[1]['last_name'])
            if i[1]['role'] == 'Dealer':
                self.dealers.append(i[1]['first_name'] + " " + i[1]['last_name'])

        for i in ppl.iterrows():
            self.ppl_id = self.ppl_id.append({"person_id": i[1]['person_id'],
                                              "name": i[1]['first_name'] + " " + i[1]['last_name']},
                                             ignore_index=TRUE)

        self.player_buyin_overtime = pd.merge(
            pplreport(data_exporter(self.transactions_file)).buy_in_over_time(),
            self.ppl_id,
            how="inner",
            on="person_id") \
            .drop(["person_id"],
                  axis=1) \
            .pivot(index="datetime",
                   columns="name")["buy_in"]

        self.player_debt_overtime = pd.merge(
            pplreport(data_exporter(self.transactions_file)).debt_over_time(),
            self.ppl_id,
            how="inner",
            on="person_id") \
            .drop(["person_id"],
                  axis=1) \
            .pivot(index="datetime",
                   columns="name")["debt"]\
            .fillna(0).cumsum()

    def load_dealer_data(self):

        self.rake_by_dealer = pd.merge(
            deal(data_exporter(self.shift_file)).
                rake_over_time(),
            self.ppl_id,
            how="inner",
            on="person_id")\
            .drop(["person_id"],
                  axis=1)\
            .pivot(index="datetime",
                   columns="name")["rake"]

        self.tips_by_dealer = pd.merge(
            deal(data_exporter(self.shift_file)).
                tips_over_time(),
            self.ppl_id,
            how="inner",
            on="person_id")\
            .drop(["person_id"],
                  axis=1)\
            .pivot(index="datetime",
                   columns="name")["tips"]

    def load_chip_data(self):
        self.reconciliation_data = rec(
            data_exporter(self.transactions_file),
            data_exporter(self.shift_file),
            data_exporter(self.people_file))

        self.chips_purchased_series = self.reconciliation_data.chips_purchased()
        self.chips_cashed_series = self.reconciliation_data.chips_cashed()
        total_rake_series = self.reconciliation_data.total_rake()
        total_tips_series = self.reconciliation_data.total_tips()
        debt_outstanding_series = self.reconciliation_data.debt_outstanding_by_player()
        self.debt_outstanding_over_time = self.reconciliation_data.debt_outstanding_over_time()

        try:
            self.chips_purchased = self.chips_purchased_series[self.date]
        except KeyError:
            self.chips_purchased = 0

        try:
            self.chips_cashed = -self.chips_cashed_series[self.date]
        except KeyError:
            self.chips_cashed = 0

        try:
            self.total_rake = total_rake_series[self.session_id]
        except KeyError:
            self.total_rake = 0

        try:
            self.total_tips = total_tips_series[self.session_id]
        except KeyError:
            self.total_tips = 0

        try:
            self.chips_float = self.chips_purchased - self.chips_cashed - (self.total_rake + self.total_tips)
        except KeyError:
            self.chips_float = 0

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

    def setup_frames(self):

        # sidebar
        self.sidebar = Frame(self.root, width=self.width/10, bg='alice blue', height=self.height, relief='sunken', borderwidth=2)
        self.sidebar.grid(row = 0, column = 0, rowspan = 2, columnspan = 1)
        self.sidebar.grid_propagate(0)

        # financials
        self.fin_frame = Frame(self.root, bg='white', width=self.width * 6 / 10, height=self.height / 2)
        self.fin_frame.grid(row = 0, column = 1, rowspan = 1, columnspan = 2)
        self.fin_frame.grid_propagate(0)

        # reconciled
        self.rec_frame = Frame(self.root, bg='grey', width=self.width * 3 / 10, height=self.height / 2)
        self.rec_frame.grid(row=0, column=3, rowspan=1, columnspan=1)
        self.rec_frame.grid_propagate(0)

        # dealer reports
        self.dealer_frame = Frame(self.root, bg='blue', width=self.width * 3 / 10, height=self.height / 2)
        self.dealer_frame.grid(row=1, column=1, rowspan=1, columnspan=1)
        self.dealer_frame.grid_propagate(0)

        # player reports
        self.player_frame = Frame(self.root, bg='red', width=self.width * 6 / 10, height=self.height / 2)
        self.player_frame.grid(row=1, column=2, rowspan=1, columnspan=2)
        self.player_frame.grid_propagate(0)

    def sidebar_buttons(self):

        button_width = 13

        buying_in_button = Button(self.sidebar, width=button_width, text="Player Buy-in",
                                  bg="alice blue", activebackground='ghost white',
                                  command=self.buyin_button)
        cashing_out_button = Button(self.sidebar, width=button_width, text="Player Cash-out",
                                  bg="alice blue", activebackground='ghost white',
                                  command=self.cashout_button)
        debt_button = Button(self.sidebar, width=button_width, text="Repay Debt",
                                  bg="alice blue", activebackground='ghost white',
                                  command=self.debt_button)
        shift_button = Button(self.sidebar, width=button_width, text="Dealer Shift",
                                  bg="alice blue", activebackground='ghost white',
                                  command=self.shift_button)
        #user_button = Button(self.sidebar, width=button_width, text="Users",
        #                          bg="alice blue", activebackground='ghost white')
        #past_sessions = Button(self.sidebar, width=button_width, text="Past Sessions",
        #                       bg="alice blue", activebackground='ghost white')
        report_button = Button(self.sidebar, width=button_width, text="Show Report",
                              bg="alice blue", activebackground='ghost white',
                              command=self.change_root_geo)
        quit_button = Button(self.sidebar, width=button_width, text="Quit",
                                  bg="alice blue", activebackground='ghost white',
                                  command=self.root.destroy)

        i = 0
        buttons = [buying_in_button, cashing_out_button, debt_button,
                             shift_button, report_button#, user_button, past_sessions]\
        ]

        for button in buttons:
            button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
            button.grid(row=i, column=0, padx = 6, pady = 3)
            i += 1

        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.grid(row=i, column=0, padx=6, pady = 510)

    def buyin_button(self):
        self.transaction_id = data_exporter(self.transactions_file)['transaction_id'].max() + 1
        self.date_time = datetime.now()
        self.chip_purchase = 1
        self.root.title("Buy-In Transaction")

        self.sidebar.destroy()
        self.fin_frame.destroy()
        self.rec_frame.destroy()
        self.dealer_frame.destroy()
        self.player_frame.destroy()

        # === Create Frame
        self.currentgeo = self.root.winfo_width()
        self.root.geometry("280x150")
        self.root.update()
        self.buyin_frame = Frame(self.root)
        self.buyin_frame.grid()

        # === Email
        player_label = Label(self.buyin_frame, text="Player")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.buyin_frame)
        player_dropdown = OptionMenu(self.buyin_frame, self.player_var, *self.players)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Transaction Type Entry
        type_label = Label(self.buyin_frame, text="Transaction Type")
        type_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        type_label.grid(row=1, column=0, sticky="w")

        self.trans_type_var = StringVar(self.buyin_frame)
        type_dropdown = OptionMenu(self.buyin_frame, self.trans_type_var, "cash", "credit")
        type_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        type_dropdown.config(width=self.option_menu_width)
        type_dropdown.grid(row=1, column=1)

        # === Quantity
        quant_label = Label(self.buyin_frame, text="Quantity of Chips")
        quant_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quant_label.grid(row=2, column=0, sticky="w")

        self.quant_ent = Entry(self.buyin_frame)
        self.quant_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.quant_ent.grid(row=2, column=1)

        # === Email
        email_label = Label(self.buyin_frame, text="E-Transfer Recipient")
        email_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_label.grid(row=3, column=0, sticky="w")

        self.email_var = StringVar(self.buyin_frame)
        email_dropdown = OptionMenu(self.buyin_frame, self.email_var, "", *self.owners)
        email_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_dropdown.config(width=self.option_menu_width)
        email_dropdown.grid(row=3, column=1)

        confirm_button = Button(self.buyin_frame, text="Confirm", command=self.buyin_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        exit_button = Button(self.buyin_frame, text="Quit", command = self.buyin_quit)
        exit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        exit_button.grid(row=4, column=1, sticky="e")

    def buyin_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]
        if self.email_var.get() != "":
            email_player_id = self.ppl_id[self.ppl_id['name'] == self.email_var.get()]['person_id'].values[0]
        else:
            email_player_id = ""
        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date,
                                                    self.trans_type_var.get(),
                                                    self.quant_ent.get(),
                                                    email_player_id,
                                                    self.chip_purchase])

        if self.email_var.get() != "":

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date,
                                                        "cash",
                                                        -int(self.quant_ent.get()),
                                                        "",
                                                        0])
            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date,
                                                        "credit",
                                                        int(self.quant_ent.get()),
                                                        "",
                                                        0])

        self.buyin_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def buyin_quit(self):
        self.buyin_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def cashout_button(self):
        self.transaction_id = data_exporter(self.transactions_file)['transaction_id'].max() + 1
        self.date_time = datetime.now()
        self.chip_purchase = 0
        self.root.title("Cash-Out Transaction")

        self.sidebar.destroy()
        self.fin_frame.destroy()
        self.rec_frame.destroy()
        self.dealer_frame.destroy()
        self.player_frame.destroy()

        # === Create Frame
        self.currentgeo = self.root.winfo_width()
        self.root.geometry("260x120")
        self.root.update()
        self.cashout_frame = Frame(self.root)
        self.cashout_frame.grid()

        # === Email
        player_label = Label(self.cashout_frame, text="Player")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.cashout_frame)
        player_dropdown = OptionMenu(self.cashout_frame, self.player_var, *self.players)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Quantity
        quant_label = Label(self.cashout_frame, text="Quantity of Chips")
        quant_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quant_label.grid(row=2, column=0, sticky="w")

        self.quant_ent = Entry(self.cashout_frame)
        self.quant_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.quant_ent.grid(row=2, column=1)

        # === Email
        email_label = Label(self.cashout_frame, text="E-Transfer Sender")
        email_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_label.grid(row=3, column=0, sticky="w")

        self.email_var = StringVar(self.cashout_frame)
        email_dropdown = OptionMenu(self.cashout_frame, self.email_var, "", *self.owners)
        email_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_dropdown.config(width=self.option_menu_width)
        email_dropdown.grid(row=3, column=1)

        confirm_button = Button(self.cashout_frame, text="Confirm", command=self.cashout_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        quit_button = Button(self.cashout_frame, text="Quit", command = self.cashout_quit)
        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.grid(row=4, column=1, sticky="e")

    def cashout_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]
        if self.email_var.get() != "":
            email_player_id = self.ppl_id[self.ppl_id['name'] == self.email_var.get()]['person_id'].values[0]
        else:
            email_player_id = ""

        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date,
                                                    "cash",
                                                    -int(self.quant_ent.get()),
                                                    email_player_id,
                                                    self.chip_purchase])

        if self.email_var.get() != "":

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date,
                                                        "cash",
                                                        int(self.quant_ent.get()),
                                                        "",
                                                        self.chip_purchase])

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date,
                                                        "credit",
                                                        -int(self.quant_ent.get()),
                                                        "",
                                                        0])

        self.cashout_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def cashout_quit(self):
        self.cashout_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def debt_button(self):
        self.transaction_id = data_exporter(self.transactions_file)['transaction_id'].max() + 1
        self.date_time = datetime.now()
        self.chip_purchase = 0
        self.root.title("Debt Repayment")

        self.sidebar.destroy()
        self.fin_frame.destroy()
        self.rec_frame.destroy()
        self.dealer_frame.destroy()
        self.player_frame.destroy()

        # === Create Frame
        self.currentgeo = self.root.winfo_width()
        self.root.geometry("280x120")
        self.root.update()
        self.debt_frame = Frame(self.root)
        self.debt_frame.grid()

        # === Player
        player_label = Label(self.debt_frame, text="Player")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.debt_frame)
        player_dropdown = OptionMenu(self.debt_frame, self.player_var, *self.players)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Quantity
        quant_label = Label(self.debt_frame, text="Quantity of Chips")
        quant_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quant_label.grid(row=2, column=0, sticky="w")

        self.quant_ent = Entry(self.debt_frame)
        self.quant_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.quant_ent.grid(row=2, column=1)

        # === Email
        email_label = Label(self.debt_frame, text="E-Transfer Recipient")
        email_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_label.grid(row=3, column=0, sticky="w")

        self.email_var = StringVar(self.debt_frame)
        email_dropdown = OptionMenu(self.debt_frame, self.email_var, "", *self.owners)
        email_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_dropdown.config(width=self.option_menu_width)
        email_dropdown.grid(row=3, column=1)

        confirm_button = Button(self.debt_frame, text="Confirm", command=self.debt_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        quit_button = Button(self.debt_frame, text="Quit", command = self.debt_quit)
        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.grid(row=4, column=1, sticky="e")

    def debt_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]
        if self.email_var.get() != "":
            email_player_id = self.ppl_id[self.ppl_id['name'] == self.email_var.get()]['person_id'].values[0]
        else:
            email_player_id = ""

        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date,
                                                    "cash",
                                                    int(self.quant_ent.get()),
                                                    email_player_id,
                                                    self.chip_purchase])

        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date,
                                                    "credit",
                                                    -int(self.quant_ent.get()),
                                                    "",
                                                    self.chip_purchase])

        if self.email_var.get() != "":
            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date,
                                                        "cash",
                                                        -int(self.quant_ent.get()),
                                                        "",
                                                        0])

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date,
                                                        "credit",
                                                        int(self.quant_ent.get()),
                                                        "",
                                                        0])


        self.debt_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def debt_quit(self):
        self.debt_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def shift_button(self):
        self.shift_id = data_exporter(self.shift_file)['shift_id'].max() + 1
        self.date_time = datetime.now()
        self.root.title("Shift Reconciliation")

        self.sidebar.destroy()
        self.fin_frame.destroy()
        self.rec_frame.destroy()
        self.dealer_frame.destroy()
        self.player_frame.destroy()

        # === Create Frame
        self.currentgeo = self.root.winfo_width()
        self.root.geometry("240x130")
        self.root.update()
        self.shift_frame = Frame(self.root)
        self.shift_frame.grid()

        # === Dealer
        player_label = Label(self.shift_frame, text="Dealer")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.shift_frame)
        player_dropdown = OptionMenu(self.shift_frame, self.player_var, *self.dealers)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Starting Float
        start_label = Label(self.shift_frame, text="Starting Float")
        start_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        start_label.grid(row=1, column=0, sticky="w")

        self.start_ent = Entry(self.shift_frame)
        self.start_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.start_ent.insert(END, "1000")
        self.start_ent.grid(row=1, column=1)

        # === Ending Float
        end_label = Label(self.shift_frame, text="Ending Float")
        end_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        end_label.grid(row=2, column=0, sticky="w")

        self.end_ent = Entry(self.shift_frame)
        self.end_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.end_ent.grid(row=2, column=1)

        # === Tips Collected
        tips_label = Label(self.shift_frame, text="Tips Collected")
        tips_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        tips_label.grid(row=3, column=0, sticky="w")

        self.tips_ent = Entry(self.shift_frame)
        self.tips_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.tips_ent.grid(row=3, column=1)

        confirm_button = Button(self.shift_frame, text="Confirm", command=self.shift_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        quit_button = Button(self.shift_frame, text="Quit", command = self.shift_quit)
        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.grid(row=4, column=1, sticky="e")

    def shift_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]

        append_list_as_row(self.shift_file, [player_id,
                                             self.shift_id,
                                             self.session_id,
                                             self.date,
                                             self.start_ent.get(),
                                             self.end_ent.get(),
                                             self.tips_ent.get()])

        self.shift_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def shift_quit(self):
        self.shift_frame.destroy()
        self.main_menu()
        if self.currentgeo == 128:
            self.root.geometry("128x720")
            self.root.update()
        else:
            self.root.geometry("1280x720")
            self.root.update()

    def reconciliation(self):
        quit()

    def tabs(self):
        self.tab_parent = ttk.Notebook(self.rec_frame)
        self.chip_tab = ttk.Frame(self.tab_parent, width=self.width * 3 / 10, height=self.height / 2 - 23)
        self.chip_tab.grid_propagate(False)
        self.debt_tab = ttk.Frame(self.tab_parent, width=self.width * 3 / 10, height=self.height / 2 - 23)
        self.transact_tab = ttk.Frame(self.tab_parent, width=self.width * 3 / 10, height=self.height / 2 - 23)

        self.tab_parent.add(self.chip_tab, text="Overview")
        self.tab_parent.add(self.debt_tab, text="Outstanding Debts")
        self.tab_parent.add(self.transact_tab, text="Transactions")

        self.tab_parent.grid()

    def debt_labels(self):
        v = Scrollbar(self.debt_tab)
        v.pack(side=RIGHT, fill=Y)

        t = Text(self.debt_tab, width=0, height=21, wrap=NONE, yscrollcommand=v.set)
        t['font'] = font.Font(family=self.font_style, size=12)

        for i in self.debt_byperson:
            t.insert(END, i[0] + ": " + i[1] + "\n")
        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)

    def transact_labels(self):
        # data = pd.merge(
        #     self.ppl_id,
        #     data_exporter(self.transactions_file),
        #     how="inner",
        #     on="person_id") \
        #     .drop(["person_id"],
        #           axis=1)
        # data = data.drop([])
        # sheet = tksheet.Sheet(self.transact_tab)
        # sheet.grid()
        # sheet.set_sheet_data(data.values.tolist())
        # sheet.headers([1,2,3])
        pass

    def overview_labels(self):
        label_width = 20

        description = Label(self.chip_tab, text="Description", bg=self.bg_color, anchor="w", width=label_width)
        amount = Label(self.chip_tab, text="Amount", bg=self.bg_color, anchor="e", width=label_width)

        desc_purchased = Label(self.chip_tab, text="Chips Purchased", bg=self.bg_color, anchor="w", width=label_width)
        purchased_amt = Label(self.chip_tab, text=self.chips_purchased, bg=self.bg_color, anchor="e", width=label_width)

        desc_cashed = Label(self.chip_tab, text="Chips Cashed Out", bg=self.bg_color, anchor="w", width=label_width)
        cashed_amt = Label(self.chip_tab, text=self.chips_cashed, bg=self.bg_color, anchor="e", width=label_width)

        desc_float = Label(self.chip_tab, text="Chips in Play", bg=self.bg_color, anchor="w", width=label_width)
        float_amt = Label(self.chip_tab, text=self.chips_float, bg=self.bg_color, anchor="e", width=label_width)

        desc_rake = Label(self.chip_tab, text="Rake Collected", bg=self.bg_color, anchor="w", width=label_width)
        rake_amt = Label(self.chip_tab, text=self.total_rake, bg=self.bg_color, anchor="e", width=label_width)

        desc_tips = Label(self.chip_tab, text="Tips Collected", bg=self.bg_color, anchor="w", width=label_width)
        tips_amt = Label(self.chip_tab, text=self.total_tips, bg=self.bg_color, anchor="e", width=label_width)

        desc_debt = Label(self.chip_tab, text="Total Debt", bg=self.bg_color, anchor="w", width=label_width)
        debt_amt = Label(self.chip_tab, text=self.total_debt, bg=self.bg_color, anchor="e", width=label_width)

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
                label['font'] = font.Font(family=self.font_style, size=12)
            pair[0].grid(row=i, column=0, sticky="nw")
            pair[1].grid(row=i, column=1, sticky="nw")
            i += 1

    def fin_tabs(self):
        self.fin_tab_parent = ttk.Notebook(self.fin_frame)
        self.revenue_tab = ttk.Frame(self.fin_tab_parent, width=self.width * 6 / 10, height=self.height / 2 - 23)
        self.chips_tab = ttk.Frame(self.fin_tab_parent, width=self.width * 6 / 10, height=self.height / 2 - 23)
        self.debts_tab = ttk.Frame(self.fin_tab_parent, width=self.width * 6 / 10, height=self.height / 2 - 23)

        self.fin_tab_parent.add(self.revenue_tab, text="Revenue")
        self.fin_tab_parent.add(self.chips_tab, text="Chip Purchases and Redemptions")
        self.fin_tab_parent.add(self.debts_tab, text="Debts")

        self.fin_tab_parent.grid()

    def rev_tab(self):
        figure = plt.Figure(figsize=(8, 3.4), dpi=100)
        figure.subplots_adjust(bottom=0.09)

        ax = figure.add_subplot(111)
        fmt_week = mdates.WeekdayLocator(byweekday=0, interval=1)
        ax.xaxis.set_major_locator(fmt_week)
        fmt_day = mdates.DayLocator()
        ax.xaxis.set_minor_locator(fmt_day)

        chart_type = FigureCanvasTkAgg(figure, self.revenue_tab)
        chart_type.get_tk_widget().pack()

        self.overview_rake.plot(kind='line',
                                legend=True,
                                ax=ax,
                                label = "Total Rake Collected").grid(axis="y",
                                                                     linewidth = 0.3)
        self.overview_tips.plot(kind='line',
                                legend=True,
                                ax=ax,
                                label="Total Tips Collected").grid(axis="y",
                                                                   linewidth=0.3)

        ax.set_title('Rake Collected over Time')

    def chips_purchaseredemption_tab(self):
        figure = plt.Figure(figsize=(8, 3.4), dpi=100)
        figure.subplots_adjust(bottom=0.09)

        ax = figure.add_subplot(111)
        fmt_week = mdates.WeekdayLocator(byweekday=0, interval=1)
        ax.xaxis.set_major_locator(fmt_week)
        fmt_day = mdates.DayLocator()
        ax.xaxis.set_minor_locator(fmt_day)

        chart_type = FigureCanvasTkAgg(figure, self.chips_tab)
        chart_type.get_tk_widget().pack()

        self.chips_purchased_series.plot(kind='line',
                                legend=True,
                                ax=ax,
                                label="Chips Purchased").grid(axis="y",
                                                                   linewidth=0.3)
        self.chips_cashed_series.multiply(-1).plot(kind='line',
                                legend=True,
                                ax=ax,
                                label="Chips Redeemed").grid(axis="y",
                                                                   linewidth=0.3)

        ax.set_title('Chip Purchases and Redemptions over Time')

    def debtsovertime_tab(self):
        figure = plt.Figure(figsize=(8, 3.4), dpi=100)
        figure.subplots_adjust(bottom=0.09)

        ax = figure.add_subplot(111)
        fmt_week = mdates.WeekdayLocator(byweekday=0, interval=1)
        ax.xaxis.set_major_locator(fmt_week)
        fmt_day = mdates.DayLocator()
        ax.xaxis.set_minor_locator(fmt_day)

        chart_type = FigureCanvasTkAgg(figure, self.debts_tab)
        chart_type.get_tk_widget().pack()

        self.debt_outstanding_over_time.plot(kind='line',
                                             legend=True,
                                             ax=ax,
                                             label="New Debt").grid(axis="y",
                                                                           linewidth=0.3)

        self.debt_outstanding_over_time.cumsum().plot(kind='line',
                                                      legend=True,
                                                      ax=ax,
                                                      label="Cumulative Debt").grid(axis="y",
                                                                             linewidth=0.3)

        ax.set_title('New Debt by Day')

    def dealer_tabs(self):
        self.dealer_tab_parent = ttk.Notebook(self.dealer_frame)
        self.rake_tab = ttk.Frame(self.dealer_tab_parent, width=self.width * 3 / 10, height=self.height / 2 - 23)
        self.tips_tab = ttk.Frame(self.dealer_tab_parent, width=self.width * 3 / 10, height=self.height / 2 - 23)

        self.dealer_tab_parent.add(self.rake_tab, text="Rake")
        self.dealer_tab_parent.add(self.tips_tab, text="Tips")

        self.dealer_tab_parent.grid()

    def rake_overtime_tab(self):
        figure = plt.Figure(figsize=(4, 3.4), dpi=100)
        figure.subplots_adjust(bottom=0.09)

        ax = figure.add_subplot(111)
        fmt_week = mdates.WeekdayLocator(byweekday=0, interval=1)
        ax.xaxis.set_major_locator(fmt_week)
        fmt_day = mdates.DayLocator()
        ax.xaxis.set_minor_locator(fmt_day)

        chart_type = FigureCanvasTkAgg(figure, self.rake_tab)
        chart_type.get_tk_widget().pack()

        self.rake_by_dealer.plot(kind='line',
                                 legend=True,
                                 ax=ax)\
            .grid(axis="y", linewidth=0.3)

        ax.set_title('Rake Collected by Dealer')

    def tips_overtime_tab(self):
        figure = plt.Figure(figsize=(4, 3.4), dpi=100)
        figure.subplots_adjust(bottom=0.09)

        ax = figure.add_subplot(111)
        fmt_week = mdates.WeekdayLocator(byweekday=0, interval=1)
        ax.xaxis.set_major_locator(fmt_week)
        fmt_day = mdates.DayLocator()
        ax.xaxis.set_minor_locator(fmt_day)

        chart_type = FigureCanvasTkAgg(figure, self.tips_tab)
        chart_type.get_tk_widget().pack()

        self.tips_by_dealer.plot(kind='line',
                                 legend=True,
                                 ax=ax)\
            .grid(axis="y", linewidth=0.3)

        ax.set_title('Tips Collected by Dealer')

    def player_tabs(self):
        self.player_tab_parent = ttk.Notebook(self.player_frame)
        self.player_overview = ttk.Frame(self.player_tab_parent, width=self.width * 6 / 10,  height=self.height / 2 - 23)
        self.debt_byplayer = ttk.Frame(self.player_tab_parent, width=self.width * 6 / 10, height=self.height / 2 - 23)

        self.player_tab_parent.add(self.player_overview, text="Buy-in by Player")
        self.player_tab_parent.add(self.debt_byplayer, text="Debt by Player")

        self.player_tab_parent.grid()

    def player_overview_tab(self):
        figure = plt.Figure(figsize=(8, 3.4), dpi=100)
        figure.subplots_adjust(bottom=0.09)

        ax = figure.add_subplot(111)
        fmt_week = mdates.WeekdayLocator(byweekday=0, interval=1)
        ax.xaxis.set_major_locator(fmt_week)
        fmt_day = mdates.DayLocator()
        ax.xaxis.set_minor_locator(fmt_day)

        chart_type = FigureCanvasTkAgg(figure, self.player_overview)
        chart_type.get_tk_widget().pack()

        self.player_buyin_overtime.plot(kind='line',
                                 legend=True,
                                 ax=ax) \
            .grid(axis="y", linewidth=0.3)

        ax.legend(loc=2)

        ax.set_title('Buy-in Size by Player')

    def player_debt_tab(self):
        figure = plt.Figure(figsize=(8, 3.4), dpi=100)
        figure.subplots_adjust(bottom=0.09)

        ax = figure.add_subplot(111)
        fmt_week = mdates.WeekdayLocator(byweekday=0, interval=1)
        ax.xaxis.set_major_locator(fmt_week)
        fmt_day = mdates.DayLocator()
        ax.xaxis.set_minor_locator(fmt_day)

        chart_type = FigureCanvasTkAgg(figure, self.debt_byplayer)
        chart_type.get_tk_widget().pack()

        self.player_debt_overtime.plot(kind='line',
                                 legend=True,
                                 ax=ax) \
            .grid(axis="y", linewidth=0.3)

        ax.legend(loc=2)

        ax.set_title('New Debt by Player')

    def change_root_geo(self):
            password = "1234"
            if self.root.winfo_width() == 1280:
                self.root.geometry("128x720")
                self.root.update()
            elif self.root.winfo_width() == 128:
                randroot = Tk()
                randroot.withdraw()
                input = simpledialog.askstring(title="Password",
                                               prompt="Enter password")
                if input == password:
                    self.root.geometry("1280x720")
                    self.root.update()