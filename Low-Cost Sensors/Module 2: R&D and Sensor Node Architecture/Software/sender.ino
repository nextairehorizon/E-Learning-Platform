#include <SoftwareSerial.h>

const int PushButton = 4;      // Digital pin for the push button
int pushButtonState = 0;       // Variable to store the push button state

// Declare a new port for serial communication
SoftwareSerial mySerial(10, 11); // RX, TX

void setup()
{
  mySerial.begin(9600);        // Start serial communication
  pinMode(PushButton, INPUT);  // Set digital pin 4 as input
}

void loop()
{
  // Read and store the push button state
  pushButtonState = digitalRead(PushButton);

  // If the push button is pressed
  if (pushButtonState == HIGH)
  {
    mySerial.write('H');       // Send 'H' through the serial port (TX)
  }
  else
  {
    mySerial.write('L');       // Send 'L' through the serial port (TX)
  }
}
