import datetime
from peewee import IntegerField


class TimedeltaField(IntegerField):
    """A version of IntegerField where a number represents the number of minutes passed"""

    def adapt(self, value):
        try:
            # Return int to the database
            if isinstance(value, datetime.timedelta):
                return value.seconds // 60

            # Return timedelta to application
            elif isinstance(value, int):
                return datetime.timedelta(minutes=value)

            return value
        except ValueError:
            return value
