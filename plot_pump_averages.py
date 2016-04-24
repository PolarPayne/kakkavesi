import pymssql
import datetime
import re, time
import matplotlib.pyplot as plt #python3-pyplot
import weather
from pump_area_precipitation import getRainInmm, listPumps

apikey = ""
with open('fmi-apikey', 'r') as keyfile:
    apikey = keyfile.read()
apikey = apikey.strip()

_SERVER = '10.144.72.11:1433'
_USER = 'devuser1'
_PASSWORD = 'devuser123'

connection = pymssql.connect(_SERVER, _USER, _PASSWORD)

'''
Represents the HSY_TARGETS table. See 'HSY_Targets taulukuvaus 2016.04.21.xlsx'.
'''
class Target:

    def __init__(self, keys, vals):
        _set_model_attrs(self, keys, vals)

    def get_pump_data(self, start, end):
        if hasattr(self, 'code'):
            return get_pump_data_between(self.code, start, end)

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
def get_pump_data_between(station, start, end):
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

def get_daily_pump_data(id, data_start_date, data_end_date):
    pump_data = []
    icurrent = data_start_date
    if id not in listPumps(): raise "unknown id"
    while True:
        inext = icurrent + datetime.timedelta(days=90)
        time.sleep(0.2)
        if inext > data_end_date: inext = data_end_date
        pump_data += get_pump_data_between(id, icurrent, inext)
        icurrent = inext
        if icurrent == data_end_date: break
    hour_runtimes = [[d.sts, max(0, d.p1_run_time)] for d in pump_data if d.p1_run_time]
    day_runtimes = {}

    for data in hour_runtimes:
        dt = data[0]
        day_dt = datetime.datetime(dt.year, dt.month, dt.day)
        if day_dt not in day_runtimes:
            day_runtimes[day_dt] = 0
        if data[1] == None:
            day_runtimes[day_dt] = -1
        if day_runtimes[day_dt] == -1: break
        day_runtimes[day_dt] += data[1]

    day_runtimes = [[key, min(1440, day_runtimes[key])] for key in day_runtimes.keys() if day_runtimes[key] != -1]
    day_runtimes.sort()
    return day_runtimes

def get_daily_rainfall(id, data_start_date, data_end_date, local):
    day_rainfalls = []
    if local:
        iday = data_start_date
        while iday < data_end_date:
            inextday = iday + datetime.timedelta(days=1)
            day_rainfalls.append([iday, min(50, getRainInmm(id, iday.year, iday.month, iday.day))])
            iday = inextday
    else:
        fmidata = []
        places = ["kumpula,Helsinki", "kaisaniemi,Helsinki", "harmaja,Helsinki", "tapiola,Espoo", "nuuksio,Espoo"]
        for p in places:
            data = weather.weather(apikey, data_start_date, data_end_date, place=p)
            fmidata.append([[datetime.datetime.strptime(d, '%Y-%m-%d'), max(0, data[d]['rrday'])] for d in data])
        fmidata = [[z[0][0], sum(p[1] for p in z) / len(places)] for z in zip(*fmidata)]
        day_rainfalls = fmidata
    day_rainfalls.sort()
    return day_rainfalls

def persist_local_max(k, dates, values):
    values = [max(values[i - k:i + k]) for i in range(k, len(values) - k)]
    dates = dates[k:-k]
    return dates, values

def rolling_average(k, dates, values):
    values = [sum(values[i - k:i + k])/(2*k) for i in range(k, len(values) - k)]
    dates = dates[k:-k]
    return dates, values

def pctl(values, pct):
    sorted_vals = sorted(values)
    return sorted_vals[int(len(sorted_vals)*pct)]

def make_plot(id, data_start_date, data_end_date, local=False, test=False):
    day_runtimes = get_daily_pump_data(id, data_start_date, data_end_date)
    day_rainfalls = get_daily_rainfall(id, data_start_date, data_end_date, local)

    fig, ax1 = plt.subplots()
    plt.xticks(rotation=70)
    rainvals = [d[1] for d in day_rainfalls]
    datevals = [d[0] for d in day_rainfalls]

    if test:
        datevals, rainvals = persist_local_max(5, datevals, rainvals)

    ax1.plot(datevals, rainvals, color='#008BCE')
    k = 5

    ax1.set_xlabel('Date')
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('Helsinki rainfall (mm)', color='#008BCE')
    for tl in ax1.get_yticklabels():
        tl.set_color('#008BCE')
    ax1.set_ylim(0,50)

    ax2 = ax1.twinx()
    runtimevals = [d[1] for d in day_runtimes]
    runtimedayvals = [d[0] for d in day_runtimes]

    pc25 = pctl(runtimevals, 0.25)
    pc50 = pctl(runtimevals, 0.5)
    pc75 = pctl(runtimevals, 0.75)

    if test:
        ax2.plot([data_start_date, pc25],[data_end_date, pc25],'.',color='b')
        ax2.plot([data_start_date, pc50], [data_end_date, pc50], '--', color='b')
        ax2.plot([data_start_date, pc75], [data_end_date, pc75], '.', color='b')

    if test:
        runtimevals, runtimedayvals = persist_local_max(5, datevals, rainvals)

    ax2.plot(runtimedayvals, runtimevals, color='#D03232')

    running_avg = list(zip(*[runtimevals[i:len(runtimevals) - 2*k + i] for i in range(2*k)]))
    running_avg = [sum(v) / len(v) for v in running_avg]
    ax2.plot(runtimedayvals[k:len(runtimedayvals) - k], running_avg, '--', color='#D24D3E')

    ax2.set_ylabel('Pump runtime (min)', color='#D03232')
    for tl in ax2.get_yticklabels():
        tl.set_color('#D03232')
    #import matplotlib.dates as mdates
    #myFmt = mdates.DateFormatter('%b')
    #ax1.xaxis.set_major_formatter(myFmt)
    #plt.xticks([datetime.datetime(2015,i,1) for i in range(1,13,1)])
    fig.suptitle("Station %s, 2015" % id)
    return fig

if __name__ == "__main__":
    p = make_plot("JVP1078", datetime.datetime(2015, 1, 1), datetime.datetime(2015, 12, 31), test=False)
    plt.show()

    if False:
        for id in listPumps():
            try:
                fig = make_plot(id, datetime.datetime(2015, 1, 1), datetime.datetime(2015, 6, 1))
                fig.savefig(id + ".png")
            except: continue
