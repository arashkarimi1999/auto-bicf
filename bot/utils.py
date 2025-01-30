from datetime import datetime, timedelta
import pytz


def get_working_day():
    """
    Calculate the next working day (Monday to Friday)
    starting after 7 AM in the Europe/Berlin timezone.

    Returns:
        datetime.date: The next working day starting after 7 AM.
        int: Maximum time of the day.
    """
    now = datetime.now(pytz.timezone('Europe/Berlin'))

    if now.hour >= 7:
        now += timedelta(days=1)

    if now.weekday() == 5:
        return now.date(), 14 - 9
    
    if now.weekday() == 6:
        now += timedelta(days=1)

    return now.date(), 23 - 9
