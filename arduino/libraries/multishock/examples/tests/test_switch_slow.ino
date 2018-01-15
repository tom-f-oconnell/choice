
#include <multishock.hpp>

// TODO use? need to get library to use, right?
const unsigned int = min_demux_period_ms 1;

// TODO instructions for connects for test purposes (intra-Arduino)
const unsigned char sig_a = 44;
const unsigned char sig_b = 45;

const unsigned int period_per_channel_ms = 5000;

void setup() {
  msk::init();

  // two different signals for verifying on oscilloscope
  // which channels of the analog switch are selected (assuming chip is working)
  // TODO can any arbitrary combination of pins be manipulated independently w/
  // PWM?
  pinMode(sig_a, OUTPUT);
  pinMode(sig_b, OUTPUT);
  //analogWrite(sig_a, 125);
  //analogWrite(sig_b, 125);
  digitalWrite(sig_a, LOW);
  digitalWrite(sig_b, HIGH);
}

void loop() {
  select_input_channel(true, 1);
  delay(min_demux_period_ms);
  delay(period_per_channel_ms);
  select_input_channel(false, 1);
  delay(min_demux_period_ms);
  delay(period_per_channel_ms);
}
