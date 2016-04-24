import models
import matplotlib.pyplot as pyplot
import numpy as np


def runningMeanFast(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

start_time = "2015-11-01 00:00:00"
end_time = "2015-12-01 00:00:00"

pumps = [x for x in models.get_targets_with_pump_data(start_time, end_time)]

all_runtimes = []

length = len(pumps[0].pump_data)

for pump in pumps:
    data = models.interpolate_pump_runtimes(pump.pump_data)

    if len([x for x in data if x < 0.0 or x > 62 ]) == 0 and len(data) >= length:
        all_runtimes.append(data)


averages = []

for i in range(length):
    ith_vals = [ x[i] for x in all_runtimes]
    averages.append(sum(ith_vals) / len(all_runtimes))

pump = models.get_target("1078")
data = models.interpolate_pump_runtimes([x.p1_run_time for x in pump.get_pump_data(start_time, end_time)])

data_ra = runningMeanFast(data, 24)
averages_ra = runningMeanFast(averages, 24)

deviations = [abs(averages_ra[i] - data_ra[i]) for i in range(len(data))]

data_average = sum(data)/len(data)

data_deviations = runningMeanFast([abs(k - data_average) for k in data],24)

average_deviation = (sum(deviations)/len(deviations))
norm_deviations = runningMeanFast([abs(k - average_deviation) for k in deviations], 48)



# index = 0
# pyplot.plot(pumps[index].pump_runtimes, label=pumps[index].name)
pyplot.plot(averages_ra, label="avg")
pyplot.plot(data_ra, label=pump.name + ", " + pump.station)
pyplot.legend()
pyplot.draw()
pyplot.plot(norm_deviations, label= 'normalized deviation')
pyplot.plot(deviations, label= 'absolute deviation')
pyplot.legend()
pyplot.draw()

pyplot.show()

