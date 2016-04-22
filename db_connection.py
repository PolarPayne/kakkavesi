import pymssql

_SERVER = '10.144.72.11:1433'
_USER = 'devuser1'
_PASSWORD = 'devuser123'

connection = pymssql.connect(_SERVER, _USER, _PASSWORD)

cursor = connection.cursor()
cursor.execute("SELECT * FROM [AWR].[dbo].[HSY_TARGETS]")

rows = cursor.fetchall()

print(rows[0])