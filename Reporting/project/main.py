import pandas
import sys
import webbrowser
import os

from project.Functions import *
from project import ReconciliationReport as rec
from project import FinancialReport as fin
from project import DealerReport as deal
from project import PlayerReport as player

overview_file = os.getcwd()+"/data/overview.csv"
people_file = os.getcwd()+"/data/people.csv"
roles_file = os.getcwd()+"/data/roles.csv"
shift_file = os.getcwd()+"/data/shift.csv"
transactions_file = os.getcwd()+"/data/transactions.csv"

# === EOD Reconciliation HTML
def eodrec():
    chips_purchased = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).chips_purchased()
    chips_cashed = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).chips_cashed()
    debt_outstanding = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).debt_outstanding_by_player()
    total_rake = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).total_rake()
    total_tips = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).total_tips()
    chips_float = rec.Reconciliation(data_exporter(transactions_file), data_exporter(shift_file), data_exporter(people_file)).chips_floating()

    html_table = [["header","End of Day Reconciliation"],
                  ["chips purchased", str(chips_purchased[0])],
                  ["chips cashed", str(chips_cashed[0])],
                  ["chips out on the tables", str(chips_float[0])],
                  ["debt outstanding", str(debt_outstanding.agg("sum"))],
                  ["total rake", str(total_rake[0])],
                  ["total tips", str(total_tips[0])]]

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

    debt_byperson = [["header","Debts per Person"]]
    j = 1
    for i in debts.iterrows():
        debt_byperson.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        debt_byperson[j] = [name, str(i[1]["quantity"])]
        j += 1
    webbrowser.open(html_temp_file_generator(debt_byperson))


def financial_report():
    total_revenue = fin.FinancialReport(data_exporter(overview_file), data_exporter(transactions_file),
                                        data_exporter(roles_file), data_exporter(shift_file)).total_revenue()
    revenue_breakdown = fin.FinancialReport(data_exporter(overview_file), data_exporter(transactions_file),
                                        data_exporter(roles_file), data_exporter(shift_file)).revenue_breakdown()
    revenue_per_employee = fin.FinancialReport(data_exporter(overview_file), data_exporter(transactions_file),
                                        data_exporter(roles_file), data_exporter(shift_file)).revenue_per_employee()
    debt_outstanding = fin.FinancialReport(data_exporter(overview_file), data_exporter(transactions_file),
                                               data_exporter(roles_file),
                                               data_exporter(shift_file)).debt_outstanding()
    debt_float_ratio = fin.FinancialReport(data_exporter(overview_file), data_exporter(transactions_file),
                                               data_exporter(roles_file),
                                               data_exporter(shift_file)).debt_float_ratio()
    avg_debt_per_player = fin.FinancialReport(data_exporter(overview_file), data_exporter(transactions_file),
                                           data_exporter(roles_file),
                                           data_exporter(shift_file)).avg_debt_per_player()
    avg_age_of_debt = fin.FinancialReport(data_exporter(overview_file), data_exporter(transactions_file),
                                              data_exporter(roles_file),
                                              data_exporter(shift_file)).avg_age_of_debt()

    html_table = [["header","Financial Report"],
                  ["total revenue", str(total_revenue[1])],
                  ["revenue breakdown", str(revenue_breakdown[1])],
                  ["revenue per employee", str(revenue_per_employee[1])],
                  ["debt outstanding", str(debt_outstanding)],
                  ["debt to float ratio", str(debt_float_ratio[1])],
                  ["avg_debt_per_player", str(avg_debt_per_player)],
                  ["avg_age_of_debt", str(avg_age_of_debt)]]

    webbrowser.open(html_temp_file_generator(html_table))

def dealer_report():
    rake_tips_over_time = deal.DealerReport(data_exporter(shift_file)).rake_tips_over_time()
    rake = pd.merge(data_exporter(people_file),
                     rake_tips_over_time,
                     how="inner",
                     on="person_id").drop(["person_id",
                                           "phone_num",
                                           "email",
                                           "address"], axis=1)

    html_file = [["header", "Rake by Dealer"]]
    j = 1
    for i in rake.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["rake"])]
        j += 1
    webbrowser.open(html_temp_file_generator(html_file))

def dealer_shifts():
    total_shifts = deal.DealerReport(data_exporter(shift_file)).shifts_over_time()
    shifts = pd.merge(data_exporter(people_file),
                      total_shifts,
                      how="inner",
                      on="person_id").drop(["person_id",
                                            "phone_num",
                                            "email",
                                            "address"], axis=1)

    html_file = [["header", "Number of shifts by Dealer"]]
    j = 1
    for i in shifts.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["shifts"])]
        j += 1
    webbrowser.open(html_temp_file_generator(html_file))

def avg_rake_shift():
    avg_rake = deal.DealerReport(data_exporter(shift_file)).avg_rake_per_shift()
    rakes = pd.merge(data_exporter(people_file),
                      avg_rake,
                      how="inner",
                      on="person_id").drop(["person_id",
                                            "phone_num",
                                            "email",
                                            "address"], axis=1)

    html_file = [["header", "Average rake per shift by Dealer"]]
    j = 1
    for i in rakes.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["avg_rake"])]
        j += 1
    webbrowser.open(html_temp_file_generator(html_file))

avg_rake_shift()

def player_report():
    buy_in = player.PlayerReport(data_exporter(transactions_file), data_exporter(shift_file)).buy_in_over_time()
    #avg_buy_in = player.PlayerReport(data_exporter(transactions_file), data_exporter(shift_file)).average_buy_in()
    debt_outstanding_over_time = player.PlayerReport(data_exporter(transactions_file), data_exporter(shift_file)).debt_outstanding_over_time()
    print(debt_outstanding_over_time)

player_report()