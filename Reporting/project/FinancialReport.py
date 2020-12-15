import pandas as pd
from datetime import datetime
import os
import csv


class FinancialReport:

    def __init__(self, overview, transactions, roles, shifts):
        self.overview = overview
        self. transactions = transactions
        self.roles = roles
        self.shifts = shifts

    def total_revenue(self): # would I want to group by gameday ID here?
        rake_collected = self.overview.groupby(["session_id"])["rake_collected"].agg("sum")
        tips_collected = self.overview.groupby(["session_id"])["tips_collected"].agg("sum")
        return rake_collected + tips_collected

    def revenue_breakdown(self): # % tips per rake
        rake_collected = self.overview.groupby(["session_id"])["rake_collected"].agg("sum")
        tips_collected = self.overview.groupby(["session_id"])["tips_collected"].agg("sum")
        return (tips_collected/rake_collected)*100

    def revenue_per_employee(self):
        rake_collected = self.overview.groupby(["session_id"])["rake_collected"].agg("sum")
        tips_collected = self.overview.groupby(["session_id"])["tips_collected"].agg("sum")
        employees = self.roles.groupby("role")["person_id"].nunique()
        return self.total_revenue()/employees["Dealer"]

    def debt_outstanding(self):
        chip_purchase = self.transactions[self.transactions["chip_purchase"] == 1]
        return (chip_purchase.groupby(["transaction_type"])["quantity"].agg("sum"))["credit"]

    def debt_float_ratio(self):
        end_float = self.shifts.groupby(["datetime"])["end_float"].agg("sum")
        chip_purchase = self.transactions[self.transactions["chip_purchase"] == 1]
        return (chip_purchase/end_float)*100

    def debt_float_ratio(self):
        return self.debt_outstanding()/self.total_revenue()

    def avg_debt_per_player(self):
        players = self.roles.groupby("role")["person_id"].nunique()
        return self.debt_outstanding()/players["Player"]

    def avg_age_of_debt(self):
        avg_age = 0
        age_of_debt = self.transactions[(self.transactions["transaction_type"] == "credit") &
                                        (self.transactions["chip_purchase"] == 1)]
        for i in age_of_debt["datetime"]:
            time_diff = (datetime.today() - datetime.strptime(i, "%Y-%m-%d"))
            avg_age = avg_age + time_diff.days

        return avg_age/len(age_of_debt)


