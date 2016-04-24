import requests
import xml.etree.ElementTree as ET


def group(lst, n):
    """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]

    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.

    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    """
    return list(zip(*[lst[i::n] for i in range(n)]))


def weather(api_key, start_time=None, end_time=None, place="Helsinki"):
    """
    Returns a dictionary that looks like
    -> {date: {"rrday": float, "snow": float, "tmin": float, "tmax": float, "tday": float}, ...}

    Where:
    date = yyyy-mm-dd
    rrday = precipitation during last 24 hours
    snow = snow depth
    tmin = min temperature
    tmax = max temperature
    tday = avg temperature
    """
    payload = {"request": "getFeature",
               "storedquery_id": "fmi::observations::weather::daily::simple",
               "place": place,
               }

    if start_time:
        payload["starttime"] = start_time
    if end_time:
        payload["endtime"] = end_time

    r = requests.get("http://data.fmi.fi/fmi-apikey/" + api_key +"/wfs", params=payload)

    root = ET.fromstring(r.text)

    data = ""

    for i in root.iter():
        if "Time" in i.tag:
            data += i.text[:10] + " "
        if "ParameterName" in i.tag:
            data += i.text + " "
        if "ParameterValue" in i.tag:
            data += i.text + "\n"

    data = group(data.split(), 3)

    out = {}
    for i in data:
        if i[0] not in out:
            out[i[0]] = {}
        out[i[0]][i[1]] = float(i[2])

    return out

if __name__ == "__main__":
    from sys import argv
    data = weather(argv[1], "2015-01-01", "2015-12-31")

    for i, j in data.items():
        print(i, j)

    for i in range(1, 15):
        print("2015-11-" + str(i).zfill(2), data["2015-11-" + str(i).zfill(2)])

    ma = 0
    for i, j in data.items():
        ma = j["rrday"] if j["rrday"] > ma else ma
    print(ma)

    data["2015-01-05"]["tmax"]
