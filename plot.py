import models
import matplotlib.pyplot as pyplot



pumps = [x for x in models.get_targets() if x.name != None]
start_time = "2016-04-22 12:00:00"
end_time = "2016-04-23 12:00:00"

all_runtimes = []

length = len(pumps[0].get_pump_data(start_time, end_time))

for pump in pumps:
    data = pump.get_pump_data(start_time, end_time)
    if len(data) == length:
        pump.pump_runtimes = [x.p1_run_time for x in data]
        if len([x for x in pump.pump_runtimes if type(x) != float or x > 62]) == 0:
            all_runtimes.append(pump.pump_runtimes)

averages = []

for i in range(len(pumps[0].pump_runtimes)):
    ith_vals = [ x[i] for x in all_runtimes]
    averages.append(sum(ith_vals) / len(all_runtimes))

print(len(all_runtimes))
print(averages)

pyplot.plot(averages, label="avg")
pyplot.plot(pumps[0].pump_runtimes, label=pumps[0].name)
pyplot.legend()
pyplot.show()

