/*
  DigitalReadSerial

  Reads a digital input on pin 2 and prints the result
  to the Serial Monitor.
*/

const int buttonPin = 2;  // Digital pin connected to the push button
int buttonState = 0;     // Variable to store the button state

void setup() {
  // Start serial communication
  Serial.begin(9600);

  // Set the button pin as input
  pinMode(buttonPin, INPUT);
}

void loop() {
  // Read the state of the button
  buttonState = digitalRead(buttonPin);

  // Print the value to the Serial Monitor
  Serial.println(buttonState);

  // Small delay to make the output easier to read
  delay(100);
}
