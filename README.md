# Weatherstation

Collects and plots data from wind and rain meters

sparkfun anemometer, wind vane, and rain gauge

## Setup

### Arduino

Compile and upload `weatherstation.ino` to an Arduino Uno

Plug in weatherstation:

| METER | PIN |
| :---: | :---: |
| ANEMOMETER | 2 |
| RAIN GUAGE | 3 |
| WIND VANE | 4 |

### Set up data collection
run:

`bash setup.sh`

Will prompt you to calibrate the wind vane by aligning it with North.
Once done, it will:

1. Start data collection by running `weatherstation_data_collection.py`

2. Create cronjob to plot the data every day at 12:01 AM

## Data Collection

Serial output: `WS WD R: 0.00 0.00 0.00`

**W**ind-**S**peed(mph) **W**ind-**D**irection(v) **R**ainfall(in/hr)

Data is stored in a pickled numpy array

[[time(sec) wind-speed(mph) wind-direction(v) rainfall(in/hr)] ...]

Plots:

* Wind radar plot
* Rainfall and wind details
