from db_connection import connection
import datetime
import re


'''
Represents the HSY_TARGETS table. See 'HSY_Targets taulukuvaus 2016.04.21.xlsx'.
'''
class Target:

    def __init__(self, keys, vals):
        _set_model_attrs(self, keys, vals)

    def get_pump_data(self, start, end):
        if hasattr(self, 'code'):
            return get_pump_data_beetween(self.code, start, end)

'''
Represents the HSY_MES_PUMP_1H table. See 'HSY - Tuntitason_tulostaulu_v03.xlsx'.
'''
class MesPumpHour:

    def __init__(self, keys, vals):
        _set_model_attrs(self, keys, vals)

    def get_target(self):
        if hasattr(self, 'station'):
            return get_target(self.station)


def get_targets():
    return _fetch_all_and_make_objects(Target, "SELECT * FROM [AWR].[dbo].[HSY_TARGETS]")

def get_pump_data(station ,hours):
    sql = "SELECT TOP " + str(hours)+ " * FROM [AWR].[dbo].[HSY_MES_PUMP_1H] WHERE STATION LIKE '"+get_full_code(station)+"' ORDER BY STS DESC"
    return _fetch_all_and_make_objects(MesPumpHour, sql)

def get_target(station):
    station = station if not re.match(r'^JVP.*$', station) else station.replace('JVP', '')
    return _fetch_all_and_make_objects(Target,  "SELECT * FROM [AWR].[dbo].[HSY_TARGETS] WHERE Code LIKE '"+ station +"'")[0]


'''
Get pump station data from HSY_MES_PUMP_1H for the time period beetween start and end. End datetime is included, start is not.
Start and end can be datetime.datetime objects or strings of the format "YYYY-MM-DD hh:mm:ss"
'''
def get_pump_data_beetween(station, start, end):
    station = get_full_code(station)

    timeStart = start.strftime('%Y-%m-%d %H:%M:%S') if isinstance(start, datetime.datetime) else start
    timeEnd = end.strftime('%Y-%m-%d %H:%M:%S') if isinstance(end, datetime.datetime) else end

    sql = "SELECT * FROM [AWR].[dbo].[HSY_MES_PUMP_1H] WHERE STATION LIKE '"+ station +"' AND STS > '"+ timeStart +"' AND STS <= '"+ timeEnd +"' ORDER BY STS DESC"
    return _fetch_all_and_make_objects(MesPumpHour, sql)


def get_full_code(station):
    station = station if re.match(r'^JVP.*$', station) else "JVP" + station
    return station


def _fetch_all_and_make_objects(cls, sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    keys = [x[0].lower() for x in cursor.description]
    rows = cursor.fetchall()
    return [cls(keys, x) for x in rows]


def _set_model_attrs(obj, keys, vals):
    for i in range(0, len(keys)):
        setattr(obj, keys[i], vals[i])

