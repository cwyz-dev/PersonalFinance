import  datetime    as  dt

def breakTimeDelta(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = delta.microseconds
    return (days, hours, minutes, seconds, microseconds)

def formatBrokenTimeDelta(days, hours, minutes, seconds, microseconds):
    oString = ""
    if (days > 0):
        oString += str(days) + " days, "
    for each in [hours, minutes, seconds]:
        oString += "{0:0=2d}".format(each) + ":"
    oString = oString[:-1] + "."
    oString += str(microseconds)[:3]
    return oString

def formatTimeDelta(delta):
    (day, hour, minute, second, microsecond) = breakTimeDelta(delta)
    return formatBrokenTimeDelta(day, hour, minute, second, microsecond)

def breakDateTime(dTime):
    year = dTime.year
    month = dTime.month
    day = dTime.day
    hour = dTime.hour
    minute = dTime.minute
    second = dTime.second
    microsecond = dTime.microsecond
    return (year, month, day, hour, minute, second, microsecond)

def formatBrokenDateTime(year, month, day, hour, minute, second, microsecond):
    return (str(year) + "-" + "{0:0=2d}".format(month) + "-" +
            "{0:0=2d}".format(day) + " " + formatBrokenTimeDelta(0, hour,
                                                                 minute, second,
                                                                 microsecond))

def formatDateTime(dTime):
    (year, month, day, hour, minute, second, microsecond) = breakDateTime(dTime)
    return formatBrokenDateTime(year, month, day, hour, minute, second,
                                microsecond)

if __name__ == '__main__':
    a = dt.datetime.now()
    print(formatDateTime(a))
    b = dt.datetime.now()
    print(formatDateTime(b))
    print(formatTimeDelta(b-a))
