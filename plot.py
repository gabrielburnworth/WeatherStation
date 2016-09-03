#!/usr/bin/env python

"""Weatherstation plots

Loads a day's data from file and creates:
    Radar plot
    Rainfall and wind detail plot
"""

# For plotting while running headless
import matplotlib
matplotlib.use('Agg')

import pickle
import sys
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib import dates

path = "/home/pi/WeatherStation/"

def find_closest(lookup_list, number):
    """Find the closest numerical key in list to provided number.
    Return the corresponding value.
    lookup_list structure: [(key, value), ...]"""
    try:
        keys = np.array(lookup_list, dtype=float)[:, 0]
        values = np.array(lookup_list, dtype=float)[:, 1]
    except ValueError:
        keys = np.array(lookup_list, dtype=str)[:, 0]
        keys = np.array(keys, dtype=float)
        values = np.array(lookup_list, dtype=str)[:, 1]
    differences = abs(keys - number)
    return values[np.argmin(differences)]

# Use date supplied in command line argument, or yesterday
try:
    date = dt.datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
except IndexError:
    date = dt.date.today() - dt.timedelta(1)

# Load data
datafile = open("{}data/WS_data_{}.pkl".format(path, date), 'rb')
datas = pickle.load(datafile)
# datas data structure:
# [[time_since_epoch(sec)  wind_speed(mph)
#   wind_direction(volts)  rainfall(in/hr)  0] [...]]

# Voltage to Angle lookup
angles = [
    # voltage, angle in degrees
    (3.84,   '0'  ),
    (1.98,  '22.5'),
    (2.25,  '45'  ),
    (0.41,  '67.5'),
    (0.45,  '90'  ),
    (0.32, '112.5'),
    (0.90, '135'  ),
    (0.62, '157.5'),
    (1.40, '180'  ),
    (1.19, '202.5'),
    (3.08, '225'  ),
    (2.93, '247.5'),
    (4.62, '270'  ),
    (4.04, '292.5'),
    (4.34, '315'  ),  # should be 4.78v
    (3.43, '337.5')
    ]

degrees = np.array(angles, dtype=float)[:, 1]  # get degrees only
angles.sort()
data = []
# data data structure: [[wind_speed(mph)  wind_direction(degrees)] [...]]
# convert wind direction: voltage to degrees
for d in datas:
    data.append([d[1], find_closest(angles, d[2])])
data = np.array(data)

voltages = list(np.array(angles, dtype=float)[:, 0])  # get voltages only

timestamp = dates.date2num(
    [dt.datetime.fromtimestamp(d) for d in datas[:, 0]])  # datetime
WindSpeed = datas[:, 1]  # wind speed
WindDirectionVoltage = datas[:, 2]  # direction voltage
WindDirectionDegrees = data[:, 1]  # direction degrees

# Create set of measured voltages
WindDirectionVoltageSet = set()
for v in WindDirectionVoltage:
    WindDirectionVoltageSet.add(v)
UniqueWindDirectionVoltages = list(WindDirectionVoltageSet)
UniqueWindDirectionVoltages.sort()

# Degrees to Cardinal Direction lookup
directions = [
 # angle (degrees), cardinal direction
    (0,     'E'  ),
    (22.5,  'ENE'),
    (45,    'NE' ),
    (67.5,  'NNE'),
    (90,    'N'  ),
    (112.5, 'NNW'),
    (135,   'NW' ),
    (157.5, 'WNW'),
    (180,   'W'  ),
    (202.5, 'WSW'),
    (225,   'SW' ),
    (247.5, 'SSW'),
    (270,   'S'  ),
    (292.5, 'SSE'),
    (315,   'SE' ),
    (337.5, 'ESE')
    ]

# Wind vane orientation calibration adjustment
try:
    with open("{}WS_calibration_data.txt".format(path), 'r') as f:
        wind_vane_offset = float(f.readlines()[0])
except IOError:
    wind_vane_offset = 0
CDs_compass = ['E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW',
       'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE']
CDs = np.array(CDs_compass, dtype=str)
CD_begin = find_closest(directions, wind_vane_offset)
CD_begin_index = np.where(CDs == CD_begin)[0][0]
CDs = np.append(CDs[CD_begin_index:],CDs[:CD_begin_index])
directions = np.array(directions, dtype=str)
directions[:, 1] = CDs

# Create list of degree directions
CompassPointDegrees = range(0, 3600, 225)
CompassPointDegrees = list(np.array(CompassPointDegrees) / 10.)
cardinal_directions = list(np.array(directions)[:, 1])

# Create list of maximum wind speeds for each direction
max_wind_speed = []
for a in CompassPointDegrees:  # loop through directions
    da = []  # create empty temporary list
    for d in data:  # loop thru records [wind_speed(mph)  wind_direction(deg)]
        if d[1] == a:  # if direction matches, add speed
            da.append(d[0])
    try:  # add maximum wind speed for direction to list
        max_wind_speed.append(np.max(da))
    except ValueError:  # no records for this direction
        max_wind_speed.append(0)
# Close polygon by copying first record to last point
max_wind_speed.append(max_wind_speed[0])
CompassPointDegrees_closed = list(CompassPointDegrees)
CompassPointDegrees_closed.append(CompassPointDegrees[0])

rain = datas[:, 3]

#######################
# radar plot

fig = plt.figure(figsize=(12, 12))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.75], projection="polar")
ax.set_thetagrids(degrees, labels=CDs_compass,
                       fontsize=14, weight='bold')
ax.spines["polar"].set_visible(False)

offset = round(wind_vane_offset / 22.5) * 22.5
ax.plot(np.deg2rad(data[:, 1] + offset), data[:, 0],
        "o", lw=2, ms=10, mec='g', mfc='g', alpha=0.01)
ax.plot(np.deg2rad(np.array(CompassPointDegrees_closed) + offset), max_wind_speed,
        "-", lw=2, mec="g", mfc='g', alpha=0.4)

ttl = plt.title("Weatherstation: Wind (MPH) - {}".format(date),
                weight='extra bold', fontsize='x-large')
ttl.set_position([0.5, 1.1])
fig.savefig("{}plots/WS_radar_{}".format(path, date))

##############################################
# Debug plots

fig = plt.figure(figsize=(18, 18))

#######################
# voltage plot

ax = plt.subplot2grid((8, 4), (0, 0), rowspan=5)

# Plot measured voltages
for v in UniqueWindDirectionVoltages:
    ax.plot([0, 0.5], [v, v], 'k-', lw=2)

# Plot expected voltages and corresponding cardinal directions
for v, d in zip(voltages, cardinal_directions):
    color = 'k'
    if v == 4.34:  # show voltage discrepancy
        color = 'grey'
        ax.plot([0.5, 1], [4.78, 4.78], '-', color=color, lw=2)
        ax.annotate(CDs[-2], xy=(1, 4.78), color=color, ha='left', va='center')
    ax.plot([0.5, 1], [v, v], '-', color=color, lw=2)
    ax.annotate(d, xy=(1, v), color=color, ha='left', va='center')

ax.annotate("Measured", xy=(0.25, 5), weight='bold', ha='center', va='bottom')
ax.annotate("Expected", xy=(0.75, 5), weight='bold', ha='center', va='bottom')
ax.set_ylabel("Voltage", weight='bold')
majorLocator = MultipleLocator(0.2)
ax.yaxis.set_major_locator(majorLocator)
minorLocator = MultipleLocator(0.5)
ax.xaxis.set_major_locator(minorLocator)
ax.axes.xaxis.set_ticklabels([])
ax.set_title("Wind Vane", weight='bold', y=1.02)


#######################
# time plot

def plotformat(ax):
    if ax.get_title().strip() != "Wind Direction":
        majorLocator = MultipleLocator(1)
        ax.yaxis.set_major_locator(majorLocator)
        ax.minorticks_on()
        ax.grid("on", which='minor', ls='-', alpha=0.2)
    ax.xaxis.set_major_locator(dates.HourLocator(interval=2))
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    ax.grid("on", which='major', ls='-', alpha=0.4)
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=0)

ax1 = plt.subplot2grid((8, 4), (5, 0), colspan=4)
ax1.set_title("Wind Speed", weight="bold")
ax1.plot(timestamp, WindSpeed, 'g-', lw=1)
ax1.set_xlim(date, date + dt.timedelta(1))
ax1.set_ylabel("Wind Speed (mph)", weight="bold")
plotformat(ax1)

ax2 = plt.subplot2grid((8, 4), (6, 0), rowspan=2, colspan=4)
ax2.set_title("Wind Direction", weight="bold")
ax2.plot(timestamp, WindDirectionVoltage, 'g-', lw=1)
ax2.set_ylim(0, 5)
ax2.set_xlim(date, date + dt.timedelta(1))
ax2.set_ylabel("Wind Direction (voltage)", weight="bold")
ax2.set_yticks(voltages)
ax2.tick_params(axis='y', labelsize='x-small')
for v, d in zip(voltages, cardinal_directions):
    ax2.annotate(d, xy=(timestamp[-1], v), fontsize=8, color='b', va='center')
plotformat(ax2)

ax3 = plt.subplot2grid((8, 4), (4, 1), rowspan=1, colspan=3)
ax3.set_title("Rain Guage", weight="bold")
ax3.plot(timestamp, rain, 'g-', lw=1)
ax3.set_ylim(0, 2)
ax3.set_xlim(date, date + dt.timedelta(1))
ax3.set_ylabel("Rainfall (in/hr)", weight="bold")
plotformat(ax3)

#######################
# hist plot

ax = plt.subplot2grid((8, 4), (0, 1), rowspan=4, colspan=3)

hmin, hmax = -11.25, 348.75
bins = np.arange(hmin, hmax, 22.5)

ax.hist(WindDirectionDegrees, normed=1, bins=bins, alpha=0.25)
ax.set_xlabel("Direction", weight="bold")
ax.set_ylabel("Frequency", weight="bold")
ax.set_xticks(CompassPointDegrees)
ax.set_xticklabels(cardinal_directions)
ax.set_xlim(hmin, hmax)
ax.set_title("Wind Direction Histogram", weight="bold")

plt.suptitle("Weatherstation: {}".format(date),
             weight="extra bold", fontsize='xx-large')
plt.tight_layout()
plt.subplots_adjust(top=0.92, hspace=0.6, wspace=0.5)
fig.savefig("{}plots/WS_detail-plots_{}".format(path, date))
