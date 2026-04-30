from datetime import date


def matcher():
    # conditions (in this configuration, yield all July 13th Fridays)
    month = 7
    day = 13
    weekday = 4  # Monday=0 ... Sunday=6 → Friday=4
    start_date = date(2008, 7, 13)

    year = start_date.year
    while True:
        try:
            d = date(year, month, day)
            if d >= start_date and d.weekday() == weekday:
                yield d
        except ValueError:
            pass
        year += 1


match = matcher()
while True:
    input(next(match))
