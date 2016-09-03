#!/usr/bin/env python

"""Weatherstation calibration

Gets and prints 10 data points. For use in `setup.sh`.
"""

import time
import sys
import numpy as np
import serial

filename = "calibration_data.txt"

def write(text):
    with open(filename, 'w') as outputfile:
        outputfile.write('%s'%text)


def printheader():
    print ""
    print ""
    print '%s%s'%(" " * 6,
                  "    Time       Wind Speed   Wind Direction   Rain Gauge")
    print '%s%s'%(" " * 6,
                  "                  (mph)       (degrees)        (in/hr)")
    print '%s%s'%(" " * 6, "-" * 60)


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

try:
    ser = serial.Serial('/dev/ttyACM0', 9600)
except serial.serialutil.SerialException:
    print
    print "Serial Error: no connection to /dev/ttyACM0 at 9600"
    print
    sys.exit()
printheader()
output_count = 10  # for calibration, print first n data lines

while output_count > 1:
    output_count -= 1
    time.sleep(0.5)
    StartTime = time.time()
    try:
        data = ser.readline()
    except (serial.serialutil.SerialException, NameError):
        print "Serial Error"
        continue
    time.sleep(0.5)
    if data[0] == 'W':
        dataR = data.strip().split()
        try:
            WindSpeed = float(dataR[3])
            WindDirectionVoltage = float(dataR[4])
            Rainfall = float(dataR[5])
        except (IndexError, ValueError, NameError):
            print "Could not read data"
            continue
        DataTime = time.time()
        CurrentTime = time.localtime()
        FormattedTime = time.strftime('%H:%M:%S', CurrentTime)
        WindDirectionDegrees = find_closest(angles, WindDirectionVoltage)
        record = [FormattedTime, WindSpeed, WindDirectionDegrees, Rainfall]
        if output_count == 1:
            write(WindDirectionDegrees)
            print
            print "Selected wind vane North offset angle: {} degrees".format(
                WindDirectionDegrees)
            print
            sys.exit()
        print "{s:8}{:9}{:11.2f}{:14.2f}{:15.2f}{s:11}({tts:.1f} sec)".format(
            *record,
            s=" ",
            tts=(DataTime - StartTime))
