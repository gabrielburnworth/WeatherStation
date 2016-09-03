/* Arduino sketch for the Weather Meter Kit from Sparkfun.
 (sparkfun.com/products/8942)

 =========================================================
 ANEMOMETER
 =========================================================
 The anemometer (wind speed meter) encodes the wind speed
 by simply closing a switch with each rotation. A wind
 speed of 1.492 MPH produces one switch closure per
 second.

 =========================================================
 WIND DIRECTION VANE
 =========================================================
 The wind vane reports wind direction as a voltage which
 is produced by the combination of resistors inside the
 sensor. The vane’s magnet may close two switches at once,
 allowing up to 16 different positions to be indicated.

 =========================================================
 RAIN GAUGE
 =========================================================
 The rain gauge is a self-emptying bucket-type rain gauge
 which activates a momentary button closure for each 0.011"
 of rain collected.

 */

#define PIN_ANEMOMETER  2 // Arduino Uno Interrupt Pin 0
#define PIN_RAIN_GAUGE  3 // Arduino Uno Interrupt Pin 1
#define PIN_WIND_VANE  A0

// wind speed and rainfall calculation frequency (milliseconds)
#define MSECS_CALC 5000

volatile int numRevsAnemometer;  // Incremented in the interrupt
volatile int numRainBucketDumps; // Incremented in the interrupt

//=======================================================
// Initialize
//=======================================================
void setup() {
  Serial.begin(9600);

  pinMode(PIN_ANEMOMETER, INPUT);
  digitalWrite(PIN_ANEMOMETER, HIGH);
  attachInterrupt(0, countAnemometer, FALLING);

  pinMode(PIN_RAIN_GAUGE, INPUT);
  digitalWrite(PIN_RAIN_GAUGE, HIGH);
  attachInterrupt(1, countRainGauge, FALLING);

}

//=======================================================
// Main loop
//=======================================================
void loop() {
  numRevsAnemometer = 0;
  numRainBucketDumps = 0;

  interrupts();
  delay (MSECS_CALC);
  noInterrupts();

  calcAndDisplay();
}

//=======================================================
// Interrupt handler for anemometer. Called each time the
// switch closes (one revolution).
//=======================================================
void countAnemometer() {
  numRevsAnemometer++;
}

//=======================================================
// Interrupt handler for rain gauge. Called each time the
// button closes (one bucket dump).
//=======================================================
void countRainGauge() {
  numRainBucketDumps++;
}

//=======================================================
// Calculate the wind speed, wind direction, rainfall,
// and display them
// anemometer: 1 rev/sec = 1.492 mph
// rain gauge: 1 bucket dump = 0.011 inches rain
//=======================================================
void calcAndDisplay() {

  // Calculate

  // Wind Speed (mph)
  // rev / msec * (1.492 MPH/rev * 1000 msec * 100)
  long wspeed = 149200;
  wspeed *= numRevsAnemometer;
  wspeed /= MSECS_CALC;

  // Wind Direction
  int sensorValue = analogRead(PIN_WIND_VANE);
  float voltage = sensorValue * (5.0 / 1023.0);

  // Rainfall (in/hr)
  // dumps / msec * (0.011 in/sec * 1000 msec * 3600 sec/hr * 100)
  long rain = 3960000;
  rain *= numRainBucketDumps;
  rain /= MSECS_CALC;


  // Display

  Serial.print("WS WD R: ");

  // Wind Speed
  Serial.print(float(wspeed) / 100, 2);
  Serial.print(' ');

  // Wind Direction
  Serial.print(voltage, 2);
  Serial.print(' ');

  // Rainfall
  Serial.println(float(rain) / 100, 2);
}
