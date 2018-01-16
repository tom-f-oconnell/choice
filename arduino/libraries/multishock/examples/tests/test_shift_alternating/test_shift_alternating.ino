
#include <multishock.hpp>

// TODO maybe redefine shiftreg_period_ms to be at least a few ms for this test
// in such a way that the internal multishock code uses the value set here
// or maybe make a helper function to set it?

const unsigned int interdigit_shift_period_ms = 500;

void setup() {
  Serial.begin(9600);
  msk::init();
  pinMode(LED_BUITLIN, OUTPUT);
}

void loop() {
  Serial.println("shifting in a 1");
  digitalWrite(LED_BUILTIN, HIGH);
  // TODO update to actually use library calls
  // maybe use function names for these to hint they are internals and should
  // not be used?
  shift_in(1);
  update_output();
  delay(interdigit_shift_period_ms);

  Serial.println("shifting in a 0");
  digitalWrite(LED_BUILTIN, LOW);
  shift_in(0);
  update_output();
  delay(interdigit_shift_period_ms);
}
