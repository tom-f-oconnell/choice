
#include <multishock.hpp>

// TODO maybe redefine shiftreg_period_ms to be at least a few ms for this test
// in such a way that the internal multishock code uses the value set here
// or maybe make a helper function to set it?

const unsigned int interdigit_shift_period_ms = 500;

void setup() {
  Serial.begin(9600);
  msk::init();
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  Serial.println("shifting in a 1");
  digitalWrite(LED_BUILTIN, HIGH);
  msk::_shift(1);
  msk::_update_output();
  delay(interdigit_shift_period_ms);

  Serial.println("shifting in a 0");
  digitalWrite(LED_BUILTIN, LOW);
  msk::_shift(0);
  msk::_update_output();
  delay(interdigit_shift_period_ms);
}
