import pickle
import numpy as np
import matplotlib.pyplot as plt
from plot_fn import plot_noControl, plot_control, plot_finish
from GDRSS_fn import GDRSS_build
import scipy.io as sio

noControl = 1
control = 1

storm = '201806'
objType = 'both'
hierarchyOpt = 'NH'
ISD_arrangement = 'A'
noRangeBegin = 4
noRangeEnd = 5
if storm == '201701':
    timeBegin = 8640
    timeEnd = 1310
elif storm == '201806':
    timeBegin = 8640
    timeEnd = 259200

saveType = "pickle" # "numpy" or "pickle"
saveFileType = '.svg'

save = 0
show = 1

fileNamesBase = 'trial_' + objType + '_' + storm + '_' + hierarchyOpt + '_' + ISD_arrangement

if hierarchyOpt == 'NH':
    hierarchy = 0
else:
    hierarchy = 1

if ISD_arrangement == 'A':
    ISDs = [13,12,11,10,9,8,7,6,4,3,2]
    n_ISDs = [3,5,3]
    n_trunkline = 3

control_points, colors, labels, ustreamConduits, branchConduits, WRRFConduit = GDRSS_build(ISDs)
plotParams = {'plot': 1,
    # For colors, provide array of hex colors for each ISD
    'colors': colors,
    # For labels, provide array of strings for each ISD
    'labels': labels,
    # Enter 1 to normalize downstream flows in plots and 0 otherwise
    'normalize': 0
    }
maxes = {'max_flow_WRRF': 1., 'max_flow_dstream': 1.,
    'max_TSSLoad_WRRF': 1., 'max_TSSLoad_dstream': 1.}
ctrlParams = {'setptThres': 0,
    # For objType, enter 'flow', 'TSS', or 'both' for downstream objective type;
    # 'both' considers both objectives simulataneously, weighting based on
    # values for epsilon_flow and epsilon_TSS provided above
    'objType': objType,
    # For setpt_WRRF_flow and setpt_WRRF_TSS, enter downstram flow and TSS
    # setpoints, respectively, normalized to no control simulation results
    'setpt_WRRF_flow': 0.,
    'setpt_WRRF_TSS': 0.,
    # For contType, enter 'binary' for {0,1} gate openings or 'continuous' for [0,1]
    'contType': 'continuous',
    # For hierarchy, enter 1 to have separate markets in each branch or 0 to
    # have all control points in the same market
    'hierarchy': hierarchy
    }

if storm == '201701':
    rainData = sio.loadmat('C:/Users/Sara/Desktop/2017Rain.mat')
elif storm == '201806':
    rainData = sio.loadmat('C:/Users/Sara/Desktop/201806Rain.mat')
hours = rainData['hours']
rainfall = rainData['dataConciseDiscrete']
for i in range(noRangeBegin,noRangeEnd):
    plt.figure(i)
    plt.subplot(142)
    plt.plot(hours/24,rainfall, linestyle = '-')


for i in range(noRangeBegin,noRangeEnd):
    ## No control
    if noControl == 1:
        if saveType == "pickle":
            with open('../data/results/no_control/' + fileNamesBase + '.pkl') as f:
                time, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes['max_flow_WRRF'], maxes['max_TSSLoad_WRRF'] = pickle.load(f)
            plt.figure(i)
            plot_noControl(n_trunkline, n_ISDs, plotParams, time, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes, timeBegin, timeEnd)
        elif saveType == "numpy":
            stuff = np.load('../data/results/no_control/' + fileNamesBase + '.npy')
            plt.figure(i)
            plot_noControl(n_trunkline, n_ISDs, plotParams, stuff.item().get('time'), stuff.item().get('ustream_depths'), stuff.item().get('WRRF_flow'), stuff.item().get('WRRF_TSSLoad'), stuff.item().get('dstream_flows'), maxes, timeBegin, timeEnd)


    ## Control
    if control == 1:
        if saveType == "pickle":
            if objType == "both":
                with open('../data/results/control/' + fileNamesBase + '_' + '%02d' % (i) + '.pkl') as f:
                    ISDs, weights, time_state, time_control, ustream_depths, WRRF_flow, ctrlParams['setpt_WRRF_flow'], ctrlParams['setpt_WRRF_TSS'], maxes['max_flow_WRRF'], maxes['max_TSSLoad_WRRF'], WRRF_TSSLoad, dstream_flows, maxes['max_flow_dstream'], demands, price, gates = pickle.load(f)
                setpts_all = [0.]
            else:
                with open('../data/results/control/' + fileNamesBase + '_' + '%02d' % (i) + '.pkl') as f:
                    ISDs, weights, time_state, time_control, ustream_depths, WRRF_flow, ctrlParams['setpt_WRRF_flow'], ctrlParams['setpt_WRRF_TSS'], maxes['max_flow_WRRF'], maxes['max_TSSLoad_WRRF'], WRRF_TSSLoad, dstream_flows, setpts_all, maxes['max_flow_dstream'], demands, price, gates = pickle.load(f)
            ctrlParams['setpt_WRRF_flow'] = 195.6/447.82*ctrlParams['setpt_WRRF_flow']
            ctrlParams['setpt_WRRF_TSS'] = 1.9177/4.8736*ctrlParams['setpt_WRRF_TSS']
            plt.figure(i)
            plot_control(n_trunkline, n_ISDs, ctrlParams, plotParams, time_state, time_control, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes, setpts_all, price, demands, gates, timeBegin, timeEnd)


    plot_finish(plotParams['normalize'])

    if (control == 1) and (objType == 'both'):
        plt.suptitle('beta = ' + str(weights['beta']) + ', eps_q = ' + str(weights['epsilon_flow']) + ', eps_TSS = ' + str(weights['epsilon_TSS']))
    elif (control == 1) and (objType == 'flow'):
        plt.suptitle('beta = ' + str(weights['beta']) + ', eps_q = ' + str(weights['epsilon_flow']))
    elif (control == 1) and (objType == 'TSS'):
        plt.suptitle('beta = ' + str(weights['beta']) + ', eps_TSS = ' + str(weights['epsilon_TSS']))
    elif (control == 0) and (noControl == 1):
        plt.suptitle('No control only')

    if save == 1:
        plt.savefig('../data/results/figures/' + fileNamesBase + '_' + '%02d' % (i) + saveFileType)

    if show == 1:
        plt.show()