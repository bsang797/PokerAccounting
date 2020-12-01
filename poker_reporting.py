# Code developed by Varshu Karumuri


import pandas as pd
from datetime import date, datetime
import numpy
import glob
import os

# method to read data
# finds the path of the file that is necessary
# Args - list of tables needed for data
# return value - panda data frame of table values

def find_data(tables_required):

    all_files = tables_required
    df = []

    for i in all_files:
        df.append([i, pd.read_csv("~/Desktop/table/"+i+".csv")])
    return df


def filter_data(data, reports, filters): # add another argument that specifies a bunch of filter

    if reports == "EOD_recon":
        returned_data = EOD_recon_report(data, filters)
    elif reports == "financial_report":
        returned_data = financial_report(data, filters)
    elif reports == "player_report":
        returned_data = player_report(data, filters)
    elif reports == "dealer_report":
        returned_data = dealer_report(data, filters)

    return returned_data

#def financial_report(data, filters):
    # Revenue
    #Revenue over time - buy_in transactions - sum of quantity
    # Revenue break down (tips vs rake) - overview - sum of tips and sum of rake
    # Revenue per employee over time -
    # Revenue per player - Buy-in transactions - cash out transactions / n of players

    # Debt outstanding over time:
    # Debt outstanding over time -
    # Debt outstanding as % of float
    # Debt outstanding as % of revenue
    # Average debt per player
    # Average age of debt
def EOD_recon_report(data, filters):
    # @param (data,date)
    # set up dictionary that sets up filers and specifies information for each
    # Need to filter based on each metric
    # EOD recon report
    # Amount of chips purchased on cash/ credit - buy_in_trans -> quantity, datetime

    df = data
    res = []

    print(filters[0])
    chips_purchased = df[0][1]
    chips_purchased = chips_purchased.loc[chips_purchased["transaction_datetime"] == filters[0]]
    chips_purchased = chips_purchased.loc[chips_purchased["transaction_type"].isin(["credit", "cash"])]
    chips_purchased = sum(chips_purchased["quantity"])
    res.append(["purchased chips", chips_purchased])

    # Amount of chips still out on the tables - overview - chips purchased (-) chips redeemed
    table_chips = df[1][1]
    table_chips = table_chips.loc[table_chips["datetime"] == filters[0]]
    table_chips = sum(table_chips["chips_purchased"]) - sum(table_chips["chips_redeemed"])
    res.append(["chips on table", table_chips])

    # Total rake collected - overview - datetime, rake_collected
    rake_collected = df[1][1]
    rake_collected = rake_collected.loc[rake_collected["datetime"] == filters[0]]
    rake_collected = sum(rake_collected["rake_collected"])
    res.append(["rake collected", rake_collected])

    # Total number of chips cashed in - overview - datetime, chips redeemed
    chips_redeemed = df[1][1]
    chips_redeemed = chips_redeemed.loc[chips_redeemed["datetime"] == filters[0]]
    chips_redeemed = sum(chips_redeemed["chips_redeemed"])
    res.append(["chips_redeemed", rake_collected])

    # Total tips collected - overview - datetime, tips collected
    tips_collected = df[1][1]
    tips_collected = tips_collected.loc[tips_collected["datetime"] == filters[0]]
    tips_collected = sum(tips_collected["tips_collected"])
    res.append(["tips collected", tips_collected])

    # Debt outstanding by players/ owners - debts - person_id, quantity - come back to this one, a little confused
    debt_outstanding = df[2][1]
    credit_outstanding = df[0][1]
    credit_outstanding = credit_outstanding.loc[credit_outstanding["transaction_type"] == "credit"]
    debt_outstanding = sum(debt_outstanding["quantity"]) + sum(credit_outstanding["quantity"])
    res.append(["debt_outstanding", debt_outstanding])

    return res

def player_report(data,filters):
    # tabs_req = ["buy_in_transactions", "overview", "debts", "cash_out_transactions"]
    # Player reports
    # Buy in over time - fitler transaction quantity by Person ID - buy in transactions
    df = data
    res = []

    buy_in = df[0][1]
    buy_in = buy_in.loc[buy_in["person_id"] == filters[0]]
    buy_in = sum(buy_in["quantity"])
    res.append(["buy in over time", buy_in])

    # Average buy in - total buy in/ n of transactions by person ID - buy in transactions
    avg_buy_in = df[0][1]
    avg_buy_in = avg_buy_in.loc[avg_buy_in["person_id"] == filters[0]]
    avg_buy_in = sum(avg_buy_in["quantity"])/len(avg_buy_in)
    res.append(["average buy in", avg_buy_in])


    # Debt outsanding over time -
    debts_outstanding = df[2][1]
    debts_outstanding = debts_outstanding.loc[debts_outstanding["person_id"] == filters[0]]
    debts_outstanding = sum(debts_outstanding["quantity"])
    res.append(["debts outstanding over time", debts_outstanding])

    # Cash/credit preference - count occurances of cash or credit in buy in transactions

    payment_preference = df[0][1]
    payment_preference = payment_preference.loc[payment_preference["person_id"] == filters[0]]
    credit_pref = len(payment_preference["transaction_type"] == "credit")
    cash_pref = len(payment_preference["transaction_type"] == "cash")
   # res.append(["number of credit transactions", credit_pref])
   # res.append(["number of cash transactions", cash_pref])
    if cash_pref > credit_pref:
        preference = "Cash"
    elif credit_pref > cash_pref:
        preference = "Credit"
    else:
        preference = "Equal preference"
    res.append(["Preference", preference])


    # Average age of debt - debt table - transaction date time (-) today's date/n of transactions
    avg_age = 0
    today = date.today()
    age_of_debt = df[2][1]
    age_of_debt = age_of_debt["transaction_datetime"]
    for i in (age_of_debt):
        time_diff = (datetime.today() - datetime.strptime(i, "%Y-%m-%d"))
        avg_age = avg_age + time_diff.days
    avg_age = avg_age/len(age_of_debt)
    res.append(["average age of debt", avg_age])

    return res

def dealer_report(data, filters):
    df = data
    res = []
    # Dealer reports
    # tabs_req = ["buy_in_transactions", "overview", "debts", "shift_reconciliations"]
    # Rakes and tips collected over time - person_id, tips + delta(float) - shift recon
    rake_tips = df[3][1]
    rake_tips = rake_tips.loc[rake_tips["person_id"] == filters[0]]
    rake = sum(rake_tips["ending_float"]) - sum(rake_tips["starting_float"])
    tips = sum(rake_tips["tips"])
    rake_tips = rake + tips
    res.append(["rake and tips over time", rake_tips])

    # Average rake/tips per shift - person_id, (tips + delta(float))/nShifts - shift recon
    avg_rake_tips = df[3][1]
    avg_rake_tips = avg_rake_tips.loc[avg_rake_tips["person_id"] == filters[0]]
    rake = sum(avg_rake_tips["ending_float"]) - sum(avg_rake_tips["starting_float"])
    tips = sum(avg_rake_tips["tips"])
    avg_rake_tips = (rake + tips)/len(avg_rake_tips)
    res.append(["average rake/tips per shift", avg_rake_tips])

    # Number of shifts over time person_id, filter shift by person_id
    n_shifts = df[3][1]
    n_shifts = n_shifts.loc[n_shifts["person_id"] == filters[0]]
    n_shifts = len(n_shifts)
    res.append(["total number of shifts", n_shifts])

    return res
def generate_HTML(report, data):

    w_report = report
    w_data = data
    data_list = []
    print(w_data)
    if report == "EOD_recon":
        write_file = """<html>
                    <body>
                    <h1> End of Day Reconciliation Report </h1>
                    <p>Total purchased on cash/credit: $%d</p>
                    <p>Amount of chips cashed in for cash/credit: $%d</p>
                    <p>Total amount of chips out on the tables: $%d</p>
                    <p>Total debt outstanding: $%d</p>
                    <p>Total rake collected: $%d</p>
                    <p>Total tips collected: $%d</p>
                    </body>
                    </html> """
    elif report == "financial_report":
        write_file = """<html>
                    <body>
                    <h1> Financial Report </h1>
                    <p>Revenue over time: $%d</p>
                    <p>Revenue breakdown (tips vs. rake): $%d</p>
                    <p>Revenue per employee over time: $%d</p>
                    <p>Revenue per player: $%d</p>
                    <h2> Debts </h2>
                    <p>Debts outstanding over time: $%d</p>
                    <p>Debts outstanding as % of float: $%d</p>
                    <p>Debts outstanding as % of revenue: $%d</p>
                    <p>Average debt per player: $%d</p>
                    <p>Average age of debt: $%d</p>
                    </body>
                    </html> """
    elif report == "player_report":
        write_file = """<html>
                    <body>
                    <h1> Player report </h1>
                    <p>Buy in over time: $%d</p>
                    <p>Average buy in: $%d</p>
                    <p>Debts outstanding over time: $%d</p>
                    <p>Cash/Credit preference: %s</p>
                    <p>Average amount of debt: $%d</p>
                    </body>
                    </html> """
    elif report == "dealer_report":
        write_file = """<html>
                    <body>
                    <h1> Dealer reports </h1>
                    <p>Rakes/tips collected over time: $%d</p>
                    <p>Average rake/tips per shift: $%d</p>
                    <p>Number of shifts over time: $%d</p>
                    </body>
                    </html> """

    for i in range(0, len(w_data)):
        data_list.append(w_data[i][1])
    print(data_list)
    outfile = open("webpage.html", "w")
    outfile.write(write_file % tuple(data_list))


def main(report, filters): # argument is the report being requsted

    if report == "EOD_recon":
        tabs_req = ["buy_in_transactions", "overview", "debts"]
    elif report == "financial_report":
        tabs_req = ["buy_in_transactions", "overview", "debts"]
    elif report == "player_report":
        tabs_req = ["buy_in_transactions", "overview", "debts", "cash_out_transactions"]
    elif report == "dealer_report":
        tabs_req = ["buy_in_transactions", "overview", "debts", "shift_reconciliation"]


    data = find_data(tabs_req)
    HTML_inputs = filter_data(data, report, [filters])
    generate_HTML(report, HTML_inputs)

main("EOD_recon", "2017-05-07")