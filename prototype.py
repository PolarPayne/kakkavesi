import numpy as np
#import plotly.plotly as py
#import plotly.graph_objs as go



def build_prototype_week(activity, temperature, temperature_thresh, precip, precip_thresh, percentile):

    '''
    "dp" means 'datapoint'
    activity:
        3 dim vector of pump activity measure
        [ [ [Mon-dp1, Mon-dp2...], [Tues-dp1, Tues-dp2] ...]    week 1
            [Mon-dp1, Mon-dp2...], ...                          week 2
            ... ]

    temperature:
        vector of max temp (C) for given day
        [   [Mon-Max, Tues-Max ...]     week 1
            [Mon-Max, Tues-Max ...]     week 2
                        ] 
        (gets a third dimension added, so each dp is in it's own vector)

    temperature_thesh:
        temperature cutoff - days for which temp is <= thresh are kept, others are discarded

    precip:
        vector of precip in mm for given day
        [   [Mon-prec, Tues-prec ...]     week 1
            [Mon-prec, Tues-prec ...]     week 2
                        ] 
        (gets a third dimension added, so each dp is in it's own vector)

    precip_thresh:
       precip cutoff - days for which prec is <= thresh are kept, others are discarded 

    percentile: (gets passed to numpy.percentile as 'q' parameter):
        "q : float in range of [0,100] (or sequence of floats)
        Percentile to compute which must be between 0 and 100 inclusive."


    ---
    returns:
        average, percentile
        each is of shape 7 * resolution, where resolution = number of data points in a day
        the first 'resolution' number of points correspond to average/percentile for all Monday data points

    ##################

    NOTE:

    ***     assumption is that activity array has nans for missing values. 
                        and that temp/precip arrays have nans for missing values
    in calculating averages/percentiles, nans are not included    ***

   TODO
   handle multiple activity vectors (i.e. multiple pump stations)
    
    '''
    c = temperature
    c = c.astype('float').reshape(weeks, 7, 1) #reshape so can be multiplied
    act = activity
    act = act.astype('float')
    resolution = act.shape[2]
    prec = precip
    prec = prec.astype('float').reshape(weeks, 7, 1)#reshape so can be multiplied

    c_ones = np.where(c <= temperature_thresh)
    c_zeros = np.where(c > temperature_thresh)

    c[c_ones] = 1
    c[c_zeros] = np.nan

    prec_ones = np.where(prec <= precip_thresh)
    prec_zeros = np.where(prec > precip_thresh)

    prec[prec_ones] = 1
    prec[prec_zeros] = np.nan

    act *= prec # vals multilied by one stay same; vals mult by nan go to nan
    act *= c # same as above

    avglist = []
    tails = []
    for w in range(0, 7): #for each day of the week 
        for r in range(0, resolution): #for each of the datapoints
            t = act[:,w,r]
#            print t
            tma = np.ma.masked_where(np.isnan(t), t)

            avglist.append(np.ma.average(tma))

            t_nonans = t[~np.isnan(t)]
            tails.append(np.percentile(t_nonans, percentile))

    return avglist, tails

#### the following code generates some test data
#### with randomly chosen empty values
weeks = 150
dp = 12 #number of data points in one day
act = np.random.randint(0, 100, weeks*7*dp).reshape(weeks, 7, dp)
act_nans = np.random.choice([True, False], weeks*7*dp, p=[.2, .8]).reshape(weeks, 7, dp)
act = act.astype('float')
act[act_nans == True] = np.nan

c = np.random.randint(-5, 5, weeks*7).reshape(weeks, 7, 1)
prec = np.random.randint(0, 10, weeks*7).reshape(weeks, 7, 1)
a,s = build_prototype_week(act, c, -1, prec, 7, [2.5, 97.5])
print a, len(a)
print
print s
