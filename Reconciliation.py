import pandas as pd

class Reconciliation:
    def __init__(self, transactions, shifts, people):
        self.transaction = transactions
        self.shift = shifts
        self.people = people

    def chips_purchased(self):
        transaction_is_chip = self.transaction[self.transaction["chip_purchase"] == 1]
        chip_purchase_bydate = transaction_is_chip.groupby(["session_id"])["quantity"].agg("sum")
        return chip_purchase_bydate

    def chips_cashed(self):
        transaction_not_chip = self.transaction[self.transaction["chip_purchase"] == 0]
        chip_cashed_bydate = transaction_not_chip.groupby(["session_id"])["quantity"].agg("sum")
        return chip_cashed_bydate

    def chips_floating(self):
        return self.chips_purchased() + self.chips_cashed() - sum(self.total_rake(), self.total_tips())

    def debt_outstanding_by_player(self):
        transaction_credit = self.transaction[self.transaction["transaction_type"] == "credit"]
        debt_outstanding = transaction_credit.groupby(["person_id"])["quantity"].agg("sum")
        return debt_outstanding

    def total_rake(self):
        end_float = self.shift.groupby(["session_id"])["end_float"].agg("sum")
        start_float = self.shift.groupby(["session_id"])["start_float"].agg("sum")
        return end_float - start_float

    def total_tips(self):
        tips = self.shift.groupby(["session_id"])["tips"].agg("sum")
        return tips