from __future__ import division
import models
import collections
import numpy as np
import datetime


def get_dates(start, end):
    f = "%Y-%m-%d %H:%M:%S"
#    d_str = '06/01/2013 00:00:00'
#    end_time = '16/04/2016 23:00:00'

    tart = datetime.datetime.strptime(start, f)
    end = datetime.datetime.strptime(end, f)

    l = []
    l.append(tart)
    while True:
            
            if tart == end:
                    break
            l.append(tart + datetime.timedelta(hours=1))
            tart += datetime.timedelta(hours=1)

    date_list = [i.strftime('%m-%d-%Y %H:%M:%S') for i in l]
    return date_list

#q = get_dates('2013-01-06 00:00:00', '2016-04-16 23:00:00')

target_objects = models.get_targets()
codes = [i.code for i in target_objects]

def get_data(pump, start, end):
    '''
        returns 171 x 7 x 24 matrix, np.nans for missing data
    '''
    date_list = get_dates(start, end)
    print len(date_list)
    x = models.get_target(pump)
    print start, end

    q = x.get_pump_data(start, end)
        
    ret_dict = {i.sts : i.p1_run_time for i in q} 
    ret_dict = {i.strftime('%m-%d-%Y %H:%M:%S') : v for i, v in ret_dict.iteritems()}
    d = {}
    l = []
    c = 0 
    for i in date_list:   
            if i in ret_dict:
                if ret_dict[i] == None:
                        l.append(np.nan)
                else:
                    l.append(ret_dict[i])
            else:
                l.append(np.nan)  
    print len(l)
    
    nweeks = (len(date_list) / 7) /24
    l = np.array(l).reshape(nweeks, 7, 24)
    nans = np.where(l == None)
    l[nans] = np.nan
    return l

#'2016-11-09 00:00:00', '2016-11-15 23:00:00')
#ret = get_data('1078','2015-11-09 00:00:00', '2015-11-15 23:00:00') 
#ret = get_data('1078', '2013-01-06 00:00:00', '2016-04-16 23:00:00')
#print ret
#print ret.shape

