import datetime
from peewee import IntegerField


class TimedeltaField(IntegerField):
    """A version of IntegerField where a number represents the number of minutes passed"""

    def adapt(self, value):
        try:
            return int(value)
        except ValueError:
            return value

    def get_timedelta(self, minutes):
        return datetime.timedelta(minutes=minutes)
