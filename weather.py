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


def weather(api_key):
    """
    :return [(long, lat, unix_time), (temperature, precipitation_amount), ...]
    """
    payload = {"request": "getFeature",
               "storedquery_id": "fmi::forecast::hirlam::surface::cities::multipointcoverage",
               "parameters": "temperature,precipitationAmount",
               "place":"Helsinki",
               "bbox": "24,59,26,60",
               }

    r = requests.get("http://data.fmi.fi/fmi-apikey/" + api_key +"/wfs", params=payload)

    root = ET.fromstring(r.text)


    for i in root.iter():
        if "positions" in i.tag:
            positions = i.text
        if "doubleOrNilReasonTupleList" in i.tag:
            values = i.text

    positions = group(positions.split(), 3)
    values = group(values.split(), 2)

    return list(zip(positions, values))

if __name__ == "__main__":
    from sys import argv
    data = weather(argv[1])

    for i in data:
        print(i)
