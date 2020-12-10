import pandas as pd


class PlayerReport:

    def __init__(self, transactions, roles):
        self.transactions = transactions
        self.roles = roles

    def buy_in_over_time(self):
        buy_in = self.transactions[self.transactions["quantity"] > 0]
        return buy_in.groupby(["person_id"])["quantity"].agg("sum").reset_index(name="buy_in")

    # There are a few kinks here I need to figure out
  #  def average_buy_in(self):
  #      self.transactions["avg_buy_in"] = self.buy_in_over_time()["buy_in"]
  #      return self.transactions.groupby("person_id")["avg_buy_in"].agg("sum")

    def debt_outstanding_over_time(self):
        chip_purchase = self.transactions[(self.transactions["chip_purchase"] == 1) & (self.transactions["transaction_type"] == "credit")]
        #chip_purchase["debt"] = chip_purchase.groupby()
        self.transactions["debt"] = chip_purchase.groupby(["transaction_type"])["quantity"].agg("sum")
        print(self.transactions)
        return chip_purchase.groupby(["player_id"])["quantity"].agg("sum").reset_index(name="debt")

    def cash_credit_preference(self):
        return self.transactions.groupby(["person_id", "transaction_type"]).size()

    def gain_loss_over_time(self):
        return self.transactions.groupby(["person_id"])["quantity"].agg("sum")
