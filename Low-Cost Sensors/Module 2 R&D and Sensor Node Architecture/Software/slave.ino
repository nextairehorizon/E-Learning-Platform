#include <Wire.h>

void setup() {
  // Set pins as outputs
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);

  // Join this device to the I2C bus with address 1
  Wire.begin(1);

  // Register the event triggered when data is received
  Wire.onReceive(receiveEvent);

  // Start the serial monitor to monitor communication
  Serial.begin(9600);
}

void loop() {
  delay(300);
}

// Function executed whenever data is received from the master
// whenever the master executes the endTransmission statement.
// It receives all the information sent through Wire.write.
void receiveEvent(int howMany) {

  int pinOut = 0;
  int state = 0;

  // If two bytes are available
  if (Wire.available() == 2)
  {
    // Read the first one, which corresponds to the pin
    pinOut = Wire.read();
    Serial.print("LED ");
    Serial.println(pinOut);
  }

  // If one byte is available
  if (Wire.available() == 1)
  {
    state = Wire.read();
    Serial.print("State ");
    Serial.println(state);
  }

  // Enable/disable output
  digitalWrite(pinOut, state);
}
