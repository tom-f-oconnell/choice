
// TODO define to get pre-processor to cut out delay calls
#include <multishock.hpp>

// TODO use? need to get library to use, right?
const unsigned int = min_demux_period_ms 1;

// TODO instructions for connects for test purposes (intra-Arduino)
const unsigned char sig_a = 44;
const unsigned char sig_b = 45;

void setup() {
  msk::init();
  pinMode(sig_a, OUTPUT);
  pinMode(sig_b, OUTPUT);
  digitalWrite(sig_a, LOW);
  digitalWrite(sig_b, HIGH);
}

// TODO no delay? pre-process out? wasn't I doing that here before...?

void loop() {
  // TODO update code to use new library calls

  // it seems that for short periods (< about 1ms)
  // the time it takes to switch depends somewhat on the channel
  // (such that it spends more time on ch0, for some reason.) digitalWrite?
  // (try CD4052B 0 HIGH, 1 LOW vs CD4052B 0 LOW, 1 HIGH to see) 
  select_input_channel(true, 1);
  delay(min_demux_period_ms);
  select_input_channel(false, 1);
  delay(min_demux_period_ms);
}
