import pymssql

_SERVER = '10.144.72.11:1433'
_USER = 'devuser1'
_PASSWORD = 'devuser123'

DATA = {}

def getRainInmm(id, year, month, day):
    if not id in DATA: raise "id not in data"
    if not year in DATA[id]:
        return 0
    if not month in DATA[id][year]:
        return 0
    if not day in DATA[id][year][month]:
        return 0
    return DATA[id][year][month][day]

connection = pymssql.connect(_SERVER, _USER, _PASSWORD)

cursor = connection.cursor()
cursor.execute("SELECT * FROM [AWR].[dbo].[HSY_RAINFALL_1H]")
print(cursor.description)
rows = cursor.fetchall()

print(len(rows))

ID_COL = 0
RAIN_COL = 2
DATE_COL = 4

for row in rows:
    id = row[ID_COL]
    mm = row[RAIN_COL]
    date = row[DATE_COL]
    if id not in DATA:
        DATA[id] = {}
    if date.year not in DATA[id]:
        DATA[id][date.year] = {}
    if date.month not in DATA[id][date.year]:
        DATA[id][date.year][date.month] = {}
    if date.day not in DATA[id][date.year][date.month]:
        DATA[id][date.year][date.month][date.day] = 0
    DATA[id][date.year][date.month][date.day] += mm

# test
# Data from 01/2015 .. 03/2016 (excl. 11/2015)
print(getRainInmm("VuoSaP5", 2016, 1, 28))