import numpy as np

def mbc(ustream, dstream, setpts, uparam, dparam, n_tanks, action):
    p = (sum(uparam*ustream) + sum(dparam*(dstream-setpts)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if PS == 0:
            Qi = 0
        else:
            Qi = PD[i]/PS*setpts[0] # setpts[0] assumed to be downstream flow setpoint
        if ustream[i] == 0:
            action[i] = 0.5
        else:
            h2i = Qi/(0.61*1*np.sqrt(2*9.81*ustream[i]))
            action[i] = max(min(h2i/2,1.0),0.0)
        if ustream[i] > 0.95:
            action[i] = 1.0

    return p, PD, PS, action

def mbc_bin(ustream, dstream, setpts, uparam, dparam, n_tanks, action):
    p = (sum(uparam*ustream) + sum(dparam*(dstream-setpts)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        # Binary option 1
        #if PS == 0:
        #    Qi = 0.0
        #else:
        #    Qi = PD[i]/PS*setpts[0] # setpts[0] assumed to be downstream flow setpoint
        #if ustream[i] == 0:
        #    action[i] = 0.0
        #    action[i+n_tanks] = 1.0
        #else:
        #    h2i = Qi/(0.61*1*np.sqrt(2*9.81*ustream[i]))
        #    action[i] = max(min(h2i/2,1.0),0.0)
        #    if action[i] >= 0.5:
        #        action[i] = 1.0
        #        action[i+n_tanks] = 0.0
        #    else:
        #        action[i] = 0.0
        #        action[i+n_tanks] = 1.0
        #if ustream[i] > 0.95:
        #    action[i] = 1.0
        #    action[i+n_tanks] = 0.0
        # Binary option 2
        if PD[i] >= p:
            action[i] = 1.0 # dam down gate
            action[i+n_tanks] = 0.0 # dam up gate
        else:
            action[i] = 0.0 # dam down gate
            action[i+n_tanks] = 1.0 # dam up gate
        if ustream[i] > 0.95:
            action[i] = 1.0 # dam down gate
            action[i+n_tanks] = 0.0 # dam up gate

    return p, PD, PS, action

def perf(actual, setpt):
    x = actual-setpt*np.ones(len(actual))
    value_over = x*(x>0)

    return value_over

def TSScalc(n_tanks, tankDepth, tankDepthPrev, flow, runoffs, timeStep):
    TSSCT = np.zeros(n_tanks)
    TSSL = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        runoff = runoffs[i]
        TSSconcrunoff = 1000
        if tankDepth[i] > 0.01:
            TSSCT[i] = (timeStep*TSSconcrunoff*runoff/(timeStep*flow[i]+2000*tankDepth[i])) * np.exp(-0.05/((tankDepthPrev[i]+tankDepth[i])/2)*timeStep)
        else:
            TSSCT[i] = 0.0
        TSSL[i] = TSSCT[i] * flow[i]

    return TSSL
