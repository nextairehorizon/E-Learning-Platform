#include <SoftwareSerial.h>

const int LED = 5;  // Digital pin for the LED
char state;

// Declare a new port for serial communication
SoftwareSerial mySerial(10, 11); // RX, TX

void setup()
{
  mySerial.begin(9600);  // Start serial communication
  pinMode(LED, OUTPUT);  // Set digital pin 5 as output
}

void loop()
{
  // If data arrives through the serial port (RX)
  if (mySerial.available())
  {
    // Store the character received through the serial port (RX)
    state = mySerial.read();

    // If it is an 'H'
    if (state == 'H')
    {
      // Turn on the LED (HIGH level)
      digitalWrite(LED, HIGH);
    }

    // If it is an 'L'
    if (state == 'L')
    {
      // Turn off the LED (LOW level)
      digitalWrite(LED, LOW);
    }
  }
}
