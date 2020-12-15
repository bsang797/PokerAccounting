import pandas as pd

class DealerReport:

    def __init__(self, shifts):
        self.shifts = shifts

    def rake_tips_over_time(self):
        self.shifts["end_float"].astype(float)
        self.shifts["start_float"].astype(float)
        self.shifts["rake"] = self.shifts["end_float"] - self.shifts["start_float"]
        return self.shifts.groupby(["person_id"])["rake"].agg("sum").reset_index(name="rake")

    def shifts_over_time(self):
        self.shifts["shifts"] = self.shifts.groupby(["person_id"]).agg('size')
        return self.shifts.groupby(["person_id"])["shifts"].size().reset_index(name="shifts")

    def avg_rake_per_shift(self):
        self.shifts["avg_rake"] = self.rake_tips_over_time()["rake"]/self.shifts_over_time()["shifts"]
        return self.shifts.groupby(["person_id"])["avg_rake"].agg('sum').reset_index(name="avg_rake")
