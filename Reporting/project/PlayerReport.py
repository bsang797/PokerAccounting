import pandas as pd


class PlayerReport:

    def __init__(self, transactions, roles):
        self.transactions = transactions
        self.roles = roles

    def buy_in_over_time(self):
        buy_in = self.transactions[self.transactions["quantity"] > 0]
        return buy_in.groupby(["person_id"])["quantity"].agg("sum").reset_index(name="buy_in")

    # There are a few kinks here I need to figure out
    def average_buy_in(self):
        avg_buy_in = self.transactions[self.transactions["quantity"] > 0]
        return avg_buy_in.groupby("person_id")["quantity"].mean().reset_index(name="avg_buy_in")

    def debt_outstanding_over_time(self):
        chip_purchase = self.transactions[(self.transactions["chip_purchase"] == 1) & (self.transactions["transaction_type"] == "credit")]
        return chip_purchase.groupby(["person_id"])["quantity"].agg("sum").reset_index(name="debt")

    def cash_credit_preference(self):
        preference = self.transactions.groupby(["person_id", "transaction_type"]).size().reset_index(name="count")
        preference["preference"] = preference["transaction_type"].map(str) + '(' + preference["count"].map(str) + ')'
        return preference["preference"].astype(str).groupby(preference["person_id"]).agg(["size", ", ".join])




    def gain_loss_over_time(self):
        return self.transactions.groupby(["person_id"])["quantity"].agg("sum").reset_index(name="gain/loss")
