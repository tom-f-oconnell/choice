/* Slowly switches all inputs to the optoisolators.
 *
 * Success:
 * -Voltage on center two pins of each (white) optoisolator, on the side of the 
 *  board away from the D-Sub connector, should switch between about 0 and 5v.
 * -Voltage on center two pins, of each optoisolator, on side *close* to D-Sub
 *  connector, should also switch between about 0 and 5v, but **out of phase**.
 *  I.e. when the input is around 5 volts, the output should be around 0, and 
 *  vice versa.
 */

#include <multishock.hpp>

const unsigned int isolated_pin_test_period_ms = 3000;

void setup() {
  // sets pinMode and initial state of all pins defined in multishock.h
  // (the pins referenced below)
  // also instantiates internal variables, but we don't need that for here
  msk::init();
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(msk::ser, HIGH);
  digitalWrite(msk::srclk, HIGH);
  digitalWrite(msk::srclr, HIGH);
  digitalWrite(msk::rclk, HIGH);
  digitalWrite(msk::fet_enbl, HIGH);
  digitalWrite(msk::demux_enbl, HIGH);

  // led pin flashed w/ opposite logic, to more easily think of the 
  // inversion by the optoisolators
  digitalWrite(msk::LED_BUILTIN, LOW);
  delay(isolated_pin_test_period_ms);
  
  digitalWrite(msk::ser, LOW);
  digitalWrite(msk::srclk, LOW);
  digitalWrite(msk::srclr, LOW);
  digitalWrite(msk::rclk, LOW);
  digitalWrite(msk::fet_enbl, LOW);
  digitalWrite(msk::demux_enbl, LOW);
  digitalWrite(msk::LED_BUILTIN, HIGH);
  delay(isolated_pin_test_period_ms);
}
