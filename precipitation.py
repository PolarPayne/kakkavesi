import xml.etree.ElementTree as ET
import json

def precipitation_forecasts(name):
    tree = ET.parse("ravake/HSY_" + name + ".xml")
    root = tree.getroot()

    width, height = map(int, root.attrib["dimensions_XY"].split(","))
    classes = int(root[0].attrib["amount"])

    data = [[[ [] for _ in range(width)] for _ in range(height)] for _ in range(classes)]

    data = {}

    for i in data:
        for j in i:
            print(j)
        print()

    for a, i in enumerate(root[0]):
        for j in i:
            x, y = map(int, j.attrib["XY"].split(","))
            # list(map(float, j.attrib["values"].split(",")))
            # print(a, x, y)
            data[a][x][y] = list(map(float, j.attrib["values"].split(",")))

    print(json.dumps(data))

def precipitation_forecasts2(name):
    tree = ET.parse("ravake/HSY_" + name + ".xml")
    root = tree.getroot()

    width, height = map(int, root.attrib["dimensions_XY"].split(","))
    classes = int(root[0].attrib["amount"])

    data = [[[ [] for _ in range(width)] for _ in range(height)] for _ in range(classes)]


    for i in data:
        for j in i:
            print(j)
        print()

    for a, i in enumerate(root[0]):
        for j in i:
            x, y = map(int, j.attrib["XY"].split(","))
            # list(map(float, j.attrib["values"].split(",")))
            # print(a, x, y)
            data[a][x][y] = list(map(float, j.attrib["values"].split(",")))

    print(json.dumps(data))

if __name__ == "__main__":
    precipitation_forecasts("201201241200")