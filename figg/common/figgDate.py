from datetime import datetime as n_datetime, date as n_date, time as n_time


class FiggDate(object):
    def __init__(self, date=None, time=None, datetime=None):
        self.date = date
        self.time = time

        if datetime:
            self.date = datetime.date()
            self.time = datetime.time()

    def datetime(self):
        return n_datetime.combine(self.date, self.time)

    def __key(self):
        return (self.date, self.time)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return "%s(date = %s, time = %s)" % (self.__class__, self.date, self.time)

    def __repr__(self):
        return "%s(date = %s, time = %s)" % (self.__class__, self.date, self.time)
