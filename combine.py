import get_activity
import prototype
import weather
from sklearn.externals import joblib
import datetime
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go

dps = 7*24
x_axis = range(dps)


f = "%d/%m/%Y %H:%M:%S"
d_str = '06/01/2013 00:00:00'
end_time = '16/04/2016 00:00:00'

tart = datetime.datetime.strptime(d_str, f)
end = datetime.datetime.strptime(end_time, f)

l = []
l.append(tart)
while True:
    if tart == end:
        break
    l.append(tart + datetime.timedelta(days=1))
    tart += datetime.timedelta(days=1)

date_list = [i.strftime('%Y-%m-%d %H:%M:%S') for i in l] #
print len(date_list)

weather_dict = joblib.load('./combined_weather_dict')
print weather_dict

temp_data = []
prec_data = []
print date_list[:10]

for i in date_list:
    if i[:10] in weather_dict:
        temp_data.append(float(weather_dict[i[:10]]['tmax']))
        prec_data.append(float(weather_dict[i[:10]]['rrday']))
    else:
        temp_data.append(np.nan)
        prec_data.append(np.nan)

pump_codes = joblib.load('./pump_codes_list')

weather_data = weather.weather(None, '2013-06-01', '2016-04-16')
temp_data = np.array(temp_data, dtype=np.float32)
prec_data = np.array(prec_data, dtype=np.float32)
print temp_data
print np.nanmin(temp_data), np.nanmax(temp_data), 'temp min/max'
print np.nanmin(prec_data), np.nanmax(prec_data), 'prec min/max'
print np.nanpercentile(prec_data, [2.5, 97.5]), 'prec percentile'
print np.nanmedian(prec_data), 'precc median'

print np.nanpercentile(temp_data, [2.5, 97.5]), 'temp percentile'
print np.nanmedian(temp_data), 'temp median'

def gen_plot(activity, stds, pump,comp_start, comp_end):
    
    comp_act = get_activity.get_data(pump, comp_start, comp_end)
    print comp_act, '******'
    activity = np.array(activity, dtype=np.float32)
    stds = np.array(stds, dtype=np.float32)
    upper_bound = go.Scatter(
        name='Baseline',
        x=x_axis,
        y=activity + stds,
        mode='lines',
        marker=dict(color="444"),
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')


    trace = go.Scatter(
        name='Blockage Activity',
        x=x_axis,
        y=np.ravel(comp_act),
        mode='lines',
        line=dict(color='rgb(180, 30, 68)'),
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty')

    lower_bound = go.Scatter(
        name='',
        x=x_axis,
        y=activity - stds,
        marker=dict(color="444"),
        line=dict(width=0),
        mode='lines')

    data = [lower_bound, trace, upper_bound]

    layout = go.Layout(
        yaxis=dict(title='Pump 1 activity'),
        title='Baseline activity VS blockage activity (Kallahden pump (1078)) \n (baseline <= 2C or precip ',
        showlegend = True)
    fig = go.Figure(data=data, layout=layout)


    url = py.plot(fig, filename='pandas-continuous-error-bars')
    print url


#def gen_plot(activity, stds, pump,comp_start, comp_end):
pump_codes = ['1078']
for pump in pump_codes:
    activity = get_activity.get_data(pump, '2013-01-06 00:00:00', '2016-04-16 23:00:00')
    print activity.shape

    avg, percentiles, stds = prototype.build_prototype_week(activity, np.array(temp_data), -1.0, np.array(prec_data), .3, [10, 90])    
    gen_plot(avg, stds, pump, '2015-11-09 00:00:00', '2015-11-15 23:00:00')
    print avg, percentiles, stds
    break
