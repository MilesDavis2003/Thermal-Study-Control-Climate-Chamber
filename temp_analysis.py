import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit as cf
import math

def fitting(x,m,b):
    return m*x + b

file_path = "Temp_Data/Temp_Volt_time_data_3rd.csv"
print('Hello World')

# Run code through cleaning function first and then put it into the read_data function
def cleaning(path):
    df = pd.read_csv(path)
    df = df.drop(index=range(0,10), inplace=False)
    max_time = 1e6
    df = df[(df['time']/1000) < max_time]
    time = np.array((df['time']/1000), dtype = float)
    tempS = np.array(df['temp_S'], dtype = float)
    tempP = np.array(df['temp_P'], dtype = float)
    temp_chmbr = np.array(df['temp_chmbr'], dtype = float)
    time_stamp = np.array(df['timestamp'])
    time_stamp = np.array([round(float(i.split(':')[2]), 1) for i in time_stamp])
    time = np.array([float(i) / 3600 for i in time])
    
    min_ = min(list(tempS[5000:]))
    for i, j in enumerate(tempS[5000:]):
        if j == min_:
            kink_idx = i + 5000
            break

    # If instead the kink is a maximum, use:
    # kink_idx = np.argmax(tempS)

    y_kink = tempS[kink_idx]

    # -----------------------------
    # LINEARIZE THE POST-KINK TAIL
    # -----------------------------
    tempS_linear = tempS.copy()

    # reflect everything after kink about the kink value
    tempS_linear[kink_idx:] = 2 * y_kink - tempS[kink_idx:]

    df['temp_S'] = tempS_linear

    fig, axes = plt.subplots(2, 1, figsize = (8, 16))
    ax = axes.flatten()

    ax[0].scatter(time, (1 * tempS_linear), label = 'Chip Readout', color = 'red')
    ax[0].plot(time, temp_chmbr, label = 'Chamber Temp', color = 'blue')
    ax[0].set_ylabel('Temp [C]')
    ax[0].set_xlabel('time [Hrs]')
    ax[0].set_title(f'Series Chip')
    ax[0].legend()
    ax[0].grid(True)

    ax[1].scatter(time, tempP, label = 'Chip Readout', color = 'red')
    ax[1].plot(time, temp_chmbr, label = 'Chamber Temp', color = 'blue')
    ax[1].set_ylabel('Temp [C]')
    ax[1].set_xlabel('time [Hrs]')
    ax[1].set_title(f'Bridge Chip')
    ax[1].legend()
    ax[1].grid(True)
    plt.show()

    return df


# Argument to this function is the output of the first function
def read_data(dataF):
    df = dataF
    
    # print(df.head)
    time = np.array((df['time']/1000), dtype = float)
    tempS = np.array(df['temp_S'], dtype = float)
    tempP = np.array(df['temp_P'], dtype = float)
    temp_chmbr = np.array(df['temp_chmbr'], dtype = float)

    # Fitting for Bridge Chip
    min_temp = min(tempP)
    max_tempS = max(tempS) 
        
    time = np.array([float(i) / 3600 for i in time])
    print(time[:10])
    xrange0, xrange1 = 6000, 25000
    tempP = np.array([i - min_temp for i in tempP])
    opt, cov = cf(fitting, time[xrange0:xrange1], tempP[xrange0:xrange1])
    m, b  = opt
    print(m, b)

    # Fitting for Series Chip (Calibration)
    tempS = np.array([i - max_tempS for i in tempS])
    optS, covS = cf(fitting, time[xrange0:xrange1], tempS[xrange0:xrange1])
    mS, bS  = optS
    x = np.linspace(0, 30000, 100000)

    fig, axes = plt.subplots(2, 1, figsize = (8, 16))
    ax = axes.flatten()

    print(len(tempS), len(time))
    ax[0].scatter(time, (-1 * tempS), label = 'Chip Readout', color = 'red')
    ax[0].plot(time, temp_chmbr, label = 'Chamber Temp', color = 'blue')
    ax[0].plot(x, (-1 * fitting(x, mS, bS)), color = 'green')
    ax[0].set_ylabel('Temp [C]')
    ax[0].set_xlabel('time [Hrs]')
    ax[0].set_title(f'Series Chip, Slope = {-1 * mS:.2E}')
    ax[0].set_ylim(-5, 55)
    ax[0].set_xlim(0, 7)
    ax[0].grid(True)

    ax[1].scatter(time, tempP, label = 'Chip Readout', color = 'red')
    ax[1].plot(time, temp_chmbr, label = 'Chamber Temp', color = 'blue')
    ax[1].plot(x, fitting(x, m, b), color = 'green')
    ax[1].set_ylabel('Temp [C]')
    ax[1].set_xlabel('time [Hrs]')
    ax[1].set_title(f'Bridge Chip, Slope = {m:.2E}')
    ax[1].set_ylim(-5, 55)
    ax[1].set_xlim(0, 7)
    ax[1].grid(True)
    plt.show()

    return 0

read_data(cleaning(file_path))
