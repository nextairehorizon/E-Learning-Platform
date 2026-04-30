#include <Wire.h>

void setup() {
  // Join this device to the I2C bus
  Wire.begin();
}

byte pin[] = {2, 3, 4, 5, 6};
byte state = 0;

void loop() {
  for (int i = 0; i < 5; i++)
  {
    // Start transmission to device 1
    Wire.beginTransmission(1);

    // Send one byte: the pin to turn on
    Wire.write(pin[i]);

    // Send one byte: L sets it LOW and H sets it HIGH
    Wire.write(state);

    // Stop transmission
    Wire.endTransmission();

    // Wait 1 second
    delay(1000);
  }

  // Change the state
  if (state == 0)
  {
    state = 1;
  }
  else
  {
    state = 0;
  }
}
