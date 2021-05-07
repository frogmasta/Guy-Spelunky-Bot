import os
import re
from datetime import datetime, timedelta


def convert_date(date):
    if date is None:
        return datetime.utcnow().strftime('%Y%m%d')

    split_date = re.findall(r"[\w']+", date)
    if len(split_date) != 3:
        return "Failed"

    for (index, elem) in enumerate(split_date):
        if index < 2 and len(elem) < 2:
            split_date[index] = '0' + split_date[index]

        elif index == 2 and len(elem) != 4:
            split_date[index] = '20' + split_date[index]

    return split_date[2] + split_date[0] + split_date[1]


def old_file(date, file_name):
    last_modified = datetime.utcfromtimestamp(os.path.getmtime(file_name))

    now = datetime.utcnow()
    today = now.strftime('%Y%m%d')
    if date == today:
        if now - last_modified > timedelta(minutes=30):
            return True
        return False

    day_after = datetime.strptime(date, "%Y%m%d") + timedelta(days=1)
    if last_modified < day_after:
        return True
    return False
