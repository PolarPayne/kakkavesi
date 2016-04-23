import models
import matplotlib.pyplot as pyplot
import numpy as np


def runningMeanFast(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

pumps = [x for x in models.get_targets()]
start_time = "2015-08-08 00:00:00"
end_time = "2015-12-10 00:00:00"

all_runtimes = []

length = len(pumps[0].get_pump_data(start_time, end_time))

for pump in pumps:
    if len(all_runtimes) > 20:
        break
    print(pump.name)

    data = pump.get_pump_data(start_time, end_time)

    if len(data) == length:
        if pump.quality <= 1.0:
            pump.pump_runtimes = [x.p1_run_time for x in data]
            for i in range(len(pump.pump_runtimes)):
                if type(pump.pump_runtimes[i]) != float or pump.pump_runtimes[i] > 62 or pump.pump_runtimes[i] < 0:

                    last = pump.pump_runtimes[i-1] if not (i < 0 or type(pump.pump_runtimes[i-1]) != float) else pump.pump_runtimes[i+1]
                    next = pump.pump_runtimes[i+1] if not (i < 0 or type(pump.pump_runtimes[i+1]) != float) else pump.pump_runtimes[i-1]
                    pump.pump_runtimes[i] = (last + next)/2

            all_runtimes.append(pump.pump_runtimes)

averages = []

for i in range(len(all_runtimes[0])):
    ith_vals = [ x[i] for x in all_runtimes]
    averages.append(sum(ith_vals) / len(all_runtimes))

pump = models.get_target("1078")
data = [x.p1_run_time for x in pump.get_pump_data(start_time, end_time)]
for i in range(len(data)):
                if type(data[i]) != float or data[i] > 62 or data[i] < 0:

                    last = data[i-1] if not (i < 0 or type(data[i-1]) != float) else data[i+1]
                    next = data[i+1] if not (i < 0 or type(data[i+1]) != float) else data[i-1]
                    data[i] = (last + next)/2


data_ra = runningMeanFast(data, 12)
averages_ra = runningMeanFast(averages, 12)

deviations = [abs(averages_ra[i] - data_ra[i]) for i in range(len(data))]

data_average = sum(data)/len(data)

data_deviations = runningMeanFast([abs(k - data_average) for k in data],12)

average_deviation = (sum(deviations)/len(deviations))
norm_deviations = [abs(k - average_deviation) for k in deviations]



# index = 0
# pyplot.plot(pumps[index].pump_runtimes, label=pumps[index].name)
pyplot.plot(averages_ra, label="avg")
pyplot.plot(data_ra, label=pump.name)
pyplot.legend()
pyplot.show()
pyplot.plot(norm_deviations, label=pump.name)
pyplot.plot(deviations, label=pump.name)

pyplot.show()
pyplot.plot(data_deviations, label=pump.name)
pyplot.show()

