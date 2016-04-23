from db_connection import connection
import datetime
import re



'''
Represents the HSY_TARGETS table. See 'HSY_Targets taulukuvaus 2016.04.21.xlsx'.
'''
class Target:

    def __init__(self, keys, vals, pump_data=[]):
        _set_model_attrs(self, keys, vals)
        self.quality = self._get_quality()
        self.pump_data = pump_data

    def get_pump_data(self, start, end):
        if hasattr(self, 'station'):
            self.pump_data = get_pump_data_beetween(self.station, start, end)
            return self.pump_data

    def _get_quality(self):
        cursor = connection.cursor()
        cursor.execute("SELECT Quality FROM [AWR].[dbo].[FLOW_QUALITY] WHERE Station ='"+str(self.station)+"'")
        data = cursor.fetchall()
        if len(data) > 0 and type(data[0][0]) == float:
            return data[0][0]
        else:
            return 4.0




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

def get_targets_with_pump_data(start, end):
    targets =  _fetch_all_and_make_objects(Target, "SELECT * FROM [AWR].[dbo].[HSY_TARGETS]")
    pump_data = _get_pump_data_batch(start, end)

    for t in targets:
        t.pump_data = pump_data[t.station] if t.station in pump_data else []

    return targets


def get_pump_data(station ,hours):
    sql = "SELECT TOP " + str(hours)+ " * FROM [AWR].[dbo].[HSY_MES_PUMP_1H] WHERE STATION LIKE '"+station+"' ORDER BY STS DESC"
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

    sql = "SELECT * FROM [AWR].[dbo].[HSY_MES_PUMP_1H] WHERE STATION LIKE '"+ station +"' AND STS > '"+ timeStart +"' AND STS <= '"+ timeEnd +"' ORDER BY STS ASC"
    return _fetch_all_and_make_objects(MesPumpHour, sql)


def get_full_code(station):
    station = str(station) if re.match(r'^JVP.*$', str(station)) else "JVP" + str(station)
    return station

def _get_pump_data_batch(start, end):
    timeStart = start.strftime('%Y-%m-%d %H:%M:%S') if isinstance(start, datetime.datetime) else start
    timeEnd = end.strftime('%Y-%m-%d %H:%M:%S') if isinstance(end, datetime.datetime) else end

    sql = "SELECT * FROM [AWR].[dbo].[HSY_MES_PUMP_1H] WHERE STS > '"+ timeStart +"' AND STS <= '"+ timeEnd +"' ORDER BY STS ASC"
    hour_data = _fetch_all_and_make_objects(MesPumpHour, sql)
    dict = {}
    for v in hour_data:
        dict[v.station] = [v] if v.station not in dict else dict[v.station]+[v]

    return dict


def _fetch_all_and_make_objects(cls, sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    keys = [x[0].lower() for x in cursor.description]
    rows = cursor.fetchall()

    return [cls(keys, x) for x in rows]


def _set_model_attrs(obj, keys, vals):
    for i in range(0, len(keys)):
        setattr(obj, keys[i], vals[i])

