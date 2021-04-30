from datetime import datetime

class Reconciliation:

    def __init__(self, transactions, shifts, people):
        self.transaction = transactions
        self.shift = shifts
        self.people = people

    def chips_purchased(self):
        transaction_is_chip = self.transaction[self.transaction["chip_purchase"] == 1]
        chip_purchase_bydate = transaction_is_chip.groupby(["datetime"])["quantity"].agg("sum")
        return chip_purchase_bydate

    def chips_cashed(self):
        transaction_not_chip = self.transaction[self.transaction["chip_purchase"] == 0]
        chip_cashed_bydate = transaction_not_chip.groupby(["datetime"])["quantity"].agg("sum")
        return chip_cashed_bydate

    def debt_outstanding_by_player(self):
        transaction_credit = self.transaction[self.transaction["transaction_type"] == "credit"]
        debt_outstanding = transaction_credit.groupby(["person_id"])["quantity"].agg("sum")
        return debt_outstanding

    def debt_outstanding_over_time(self):
        transaction_credit = self.transaction[self.transaction["transaction_type"] == "credit"]
        debt_outstanding_over_time = transaction_credit.groupby(["datetime"])["quantity"].agg("sum")
        return debt_outstanding_over_time

    def total_rake(self):
        end_float = self.shift.groupby(["session_id"])["end_float"].agg("sum")
        start_float = self.shift.groupby(["session_id"])["start_float"].agg("sum")
        return end_float - start_float

    def total_tips(self):
        tips = self.shift.groupby(["session_id"])["tips"].agg("sum")
        return tips

class FinancialReport:

    def __init__(self, overview, transactions, roles, shifts):
        self.overview = overview
        self.transactions = transactions
        self.roles = roles
        self.shifts = shifts

    def total_revenue(self):
        self.shifts["rake"] = self.shifts["end_float"] - self.shifts["start_float"]
        tips_collected = self.shifts.groupby(["datetime"])["tips"].agg("sum").reset_index(name="tips")
        rake_collected = self.shifts.groupby(["datetime"])["rake"].agg("sum").reset_index(name="rake")
        return rake_collected, tips_collected

class DealerReport:

    def __init__(self, shifts):
        self.shifts = shifts

    def rake_over_time(self):
        self.shifts["end_float"].astype(float)
        self.shifts["start_float"].astype(float)
        self.shifts["rake"] = self.shifts["end_float"] - self.shifts["start_float"]
        return self.shifts.groupby(["datetime","person_id"])["rake"].agg("sum").reset_index(name="rake")

    def tips_over_time(self):
        return self.shifts.groupby(["datetime","person_id"])["tips"].agg("sum").reset_index(name="tips")

class PlayerReport:

    def __init__(self, transactions):
        self.transactions = transactions

    def buy_in_over_time(self):
        buy_in = self.transactions[self.transactions["chip_purchase"] == 1]
        return buy_in.groupby(["person_id","datetime"])["quantity"].agg("sum").reset_index(name="buy_in")

    def debt_over_time(self):
        debt = self.transactions[self.transactions["transaction_type"] == "credit"]
        return debt.groupby(["person_id", "datetime"])["quantity"].agg("sum").reset_index(name="debt")