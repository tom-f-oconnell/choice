
// TODO set jumper between the isolated 5v and the hv_+ connection
// this will make it so switching the FETs should generate voltage over each
// measurement resistor

// TODO instructions for bypassing instr/iso amps for test purposes

#include <multishock.hpp>

// hacky, to get methods that otherwise we would not have access to, for testing
// purposes.
// **DO NOT** include this .cpp in any code to run experiments or collect data.
//#include "multishock.cpp"

// TODO actually, why wasn't above working? it should have been able to find
// this, unless it was 1) ignoring files w/ non .h/.hpp extensions or 2)
// moving files to some temporary directory, and not moving the .cpp file?
// maybe alternatives.

//#define ONLY_FIRST_AND_LAST

void setup() {
  Serial.begin(9600);
  msk::init();
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.print("msk::current_signal: ");
  Serial.println(msk::current_signal);
  Serial.print("A0: ");
  Serial.println(A0);
  // TODO need to throw away any analogReads?
}

void loop() {
  const unsigned int per_fet_ms = 400;
  unsigned long measurement_sum;
  unsigned int reading_count;
  unsigned long until;

  // things seem to get more noisy on 0? (w/ at least one of two fets selected?)
  // noise could have just been something intermittent though

  for (unsigned char c_measure=0; c_measure<msk::num_channels; c_measure++) {
    Serial.print("selecting channel ");
    Serial.print(c_measure);
    Serial.println(" to measure");
    msk::_select_input_channel((msk::channel_t) c_measure);

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

      if (c_fet == c_measure) {
        Serial.print("*");
      }
      Serial.print("fet ");
      Serial.print(c_fet);

      // turn on the fet with the current index (as-if to shock that channel)
      msk::start_shock(c_fet);

      reading_count = 0;
      measurement_sum = 0;
      until = millis() + per_fet_ms;
      while (millis() <= until) {
        measurement_sum += analogRead(msk::current_signal);
        reading_count++;
      }
      // turn it back off
      msk::stop_shock(c_fet);
      Serial.print(": average of ");
      Serial.print(reading_count);
      Serial.print(" readings: ");
      Serial.print(((double) measurement_sum) / reading_count);
      if (c_fet == c_measure) {
        Serial.print("*");
      }
      Serial.println("");
    }
    Serial.println("");
  }
  // so channel 15 from one iteration and 0 from the next don't blend together 
  // if just watching on a scope
  delay(1000);
}
