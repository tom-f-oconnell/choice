
#include <multishock.hpp>

const unsigned int interdigit_shift_period_ms = 500;

void setup() {
  Serial.begin(9600);
  msk::init();
}

void loop() {
  // TODO fix to use new library calls
  Serial.println("shifting in a 1");
  shift_in(1);
  update_output();
  delay(interdigit_shift_period_ms);
  // TODO how to get # bits now?
  for (int i=0;i<msk::shift_register_bits;i++) {
    Serial.println("shifting in a 0");
    shift_in(0);
    update_output();
    delay(interdigit_shift_period_ms);
//    if (i == 5) {
//      clear_reg();
//      break;
//    }
  }
}
