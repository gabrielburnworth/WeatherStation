#!/usr/bin/env python

"""Weatherstation Data Collection

Collects data from the weather meters over a serial connection with
the Arduino. Saves data to a pickled numpy database for the current day.
"""

import time
import sys
import pickle
import datetime as dt
import numpy as np
import serial


def write(text):
    print text


def printheader():
    write("")
    write("")
    write('%s%s'%(" " * 6,
                  "    Time       Wind Speed   Wind Direction   Rain Gauge"))
    write('%s%s'%(" " * 6,
                  "                  (mph)                        (in/hr)"))
    write('%s%s'%(" " * 6, "-" * 72))


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
    with open("WS_calibration_data.txt", 'r') as f:
        wind_vane_offset = float(f.readlines()[0])
except IOError:
    wind_vane_offset = 0.0
CDs_compass = ['E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW',
               'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE']
CDs = np.array(CDs_compass, dtype=str)
CD_begin = find_closest(directions, wind_vane_offset)
CD_begin_index = np.where(CDs == CD_begin)[0][0]
CDs = np.append(CDs[CD_begin_index:], CDs[:CD_begin_index])
directions = np.array(directions, dtype=str)
directions[:, 1] = CDs

try:
    date = dt.date.today()
    datas = pickle.load(open("data/WS_data_%s.pkl"%date, 'rb'))
except (IOError, EOFError):
    datas = np.empty((0, 4))
    write("New Datafile")

try:
    ser = serial.Serial('/dev/ttyACM0', 9600)
except serial.serialutil.SerialException:
    write("Serial Error: no connection to /dev/ttyACM0 at 9600")
    sys.exit()
printheader()
prev_date = dt.date.today()
output_count = 100  # print only first n data lines

while True:
    date = dt.date.today()
    if date != prev_date:
        datas = np.empty((0, 4))
    prev_date = date
    time.sleep(0.5)
    StartTime = time.time()
    try:
        data = ser.readline()
    except serial.serialutil.SerialException:
        write("Serial Error")
        continue
    time.sleep(0.5)
    if data[0] == 'W':
        dataR = data.strip().split()
        try:
            WindSpeed = float(dataR[3])
            WindDirectionVoltage = float(dataR[4])
            Rainfall = float(dataR[5])
        except (IndexError, ValueError):
            write("Could not read data")
            continue
        DataTime = time.time()
        CurrentTime = time.localtime()
        FormattedTime = time.strftime('%H:%M:%S', CurrentTime)
        WindDirectionDegrees = find_closest(angles, WindDirectionVoltage)
        WindCardinalDirection = find_closest(directions, WindDirectionDegrees)
        record = [DataTime, WindSpeed, WindDirectionVoltage, Rainfall]
        datas = np.vstack((datas, record))
        with open("data/WS_data_%s.pkl"%date, 'wb') as df:
            pickle.dump(datas, df)
        if output_count > 0:
            write("{s:8}{:9}{:11.2f}{s:12}{:6}{:15.2f}{s:11}({tts:.1f} sec)".format(
                FormattedTime, record[1], WindCardinalDirection, record[3],
                s=" ", tts=(DataTime - StartTime)))
            output_count -= 1
