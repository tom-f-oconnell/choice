
// TODO set jumper between the isolated 5v and the hv_+ connection
// this will make it so switching the FETs should generate voltage over each
// measurement resistor

// TODO instructions for bypassing instr/iso amps for test purposes

#include <multishock.hpp>

// TODO actually, why wasn't above working? it should have been able to find
// this, unless it was 1) ignoring files w/ non .h/.hpp extensions or 2)
// moving files to some temporary directory, and not moving the .cpp file?
// maybe alternatives.

//#define ONLY_FIRST_AND_LAST

void setup() {
  // 0 up to, and including, 15
  unsigned char channel = 0;

  Serial.begin(9600);
  msk::init();
  pinMode(LED_BUILTIN, OUTPUT);

  // TODO need to throw away any analogReads?

  Serial.print("selecting channel ");
  Serial.print(channel);
  Serial.println(" to measure");
  msk::_select_input_channel(channel);
}

void loop() {
  const unsigned int per_fet_ms = 2000;
  unsigned int measurement_sum = 0;
  unsigned int reading_count = 0;
  unsigned long until;

  // TODO why is 15 apparently working, but not 0? fet / measurement?

  // things seem to get more noisy on 0? (w/ at least one of two fets selected?)
  // noise could have just been something intermittent though

  // try switching each shock delivery MOSFET, one at a time
  // and measure the output of the multiplexers
  for (unsigned char c_fet=0; c_fet<msk::num_channels; c_fet++) {
    // I only constructed two channels at the start,
    // and first I just wanted to test they were working
    #ifdef ONLY_FIRST_AND_LAST
      if (!(c_fet == 0 || c_fet == 15)) {
        continue;
      }
    #endif

    // turn on the fet with the current index (as-if to shock that channel)
    Serial.print("fet ");
    Serial.print(c_fet);
    msk::start_shock(c_fet);

    reading_count = 0;
    until = millis() + per_fet_ms;
    while (millis() <= until) {
      measurement_sum += analogRead(msk::current_signal);
      reading_count++;
    }
    Serial.print(": average of ");
    Serial.print(reading_count);
    Serial.print(" readings: ");
    Serial.println(((double) measurement_sum) / reading_count);

    // TODO it looks like there might be channel specific offset?
    // zero this in software setup in advance?

    // turn it back off
    msk::stop_shock(c_fet);
  }
  Serial.println("");
}
