# WeatherStation

Collects and plots data from wind and rain meters

[Sparkfun](https://www.sparkfun.com/products/8942) anemometer, wind vane, and rain gauge:

<img src="https://cloud.githubusercontent.com/assets/12681652/18228111/c9565408-71f2-11e6-955f-e147b627a379.jpg" width="50%">

## Setup

### Arduino

Compile and upload `weatherstation.ino` to an Arduino Uno

Plug in weatherstation:

| METER | PIN |
| :---: | :---: |
| ANEMOMETER | 2 |
| RAIN GUAGE | 3 |
| WIND VANE | A0 |

<img src="https://cloud.githubusercontent.com/assets/12681652/18228412/646dfdf2-7201-11e6-801d-6cbc37090e33.png" width="50%">

Also, see [additional documentation](#additional-documentation).

### Set up data collection

On Raspbian (Raspberry Pi):

```
sudo apt-get install python-numpy python-matplotlib python-serial
git clone https://github.com/gabrielburnworth/WeatherStation
cd WeatherStation
bash setup.sh
```

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

## Example Plots

Wind speed and direction radar plot:

<img src="https://cloud.githubusercontent.com/assets/12681652/18228113/e2e2e38c-71f2-11e6-8f55-53473b7af497.png" width="50%">

Rainfall and wind detail plots:

<img src="https://cloud.githubusercontent.com/assets/12681652/18228112/e2d878fc-71f2-11e6-8f02-3b6f455fa1e2.png" width="50%">

## Additional Documentation

[Sensor details (PDF)](http://www.sparkfun.com/datasheets/Sensors/Weather/Weather%20Sensor%20Assembly..pdf) from Sparkfun

###### Wind Vane diagram:

<img src="https://cloud.githubusercontent.com/assets/12681652/18228110/c9564b48-71f2-11e6-9ef2-b15ed961d5e0.png" width="50%">

###### Interrupt pins used:

| METER | PIN | INTERRUPT |
| :---: | :---: | :---: |
| ANEMOMETER | 2 | 0 |
| RAIN GUAGE | 3 | 1 |
