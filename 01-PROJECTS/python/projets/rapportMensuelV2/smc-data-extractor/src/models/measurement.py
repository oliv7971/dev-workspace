class Measurement:
    def __init__(self, date, values):
        self.date = date
        self.values = values

    def get_date(self):
        return self.date

    def get_values(self):
        return self.values

    def __repr__(self):
        return f"Measurement(date={self.date}, values={self.values})"