#!/bin/bash

echo
echo "Weatherstation calibration and data collection setup:"
echo "-----------------------------------------------------"
echo "Rotate wind vane by hand until it's pointing north (estimate from a map or use a compass)"
echo "Calibration script will run and collect 10 datapoints (approx. 1 minute)."
echo "The last datapoint will be chosen for the orientation."
echo "Press <Enter> when ready."
read
REPLY='n'
while [[ ! $REPLY =~ ^[Yy]$ ]]
do
  python calibrate.py
  read -p "Save? (y/n) [If not, calibration will run again.]" -n 1 -r
  echo
done

read -p "Start collecting data?" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Creating directories..."
  mkdir data
  mkdir plots

  chmod +x weatherstation_data_collection.py

  python weatherstation_data_collection.py >> weatherstation_data_collection.log 2>&1 &
  echo "Data collection has begun. Use ps aux | grep WS.py to check if running."
  chmod +x plot.py

  croncmd="~/WeatherStation/plot.py > ~/WeatherStation/plot.log 2>&1"
  cronjob="01 00 * * * $croncmd"
  echo "Creating cronjob..."
  ( crontab -l | grep -v "$croncmd" ; echo "$cronjob" ) | crontab -
fi
echo "Done."
