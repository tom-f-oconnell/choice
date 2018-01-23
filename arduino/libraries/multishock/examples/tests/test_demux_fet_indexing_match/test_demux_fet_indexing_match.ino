
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

  // TODO need to throw away any analogReads?
}

void loop() {
  const unsigned int per_fet_ms = 2000;
  unsigned int measurement_sum = 0;
  unsigned int reading_count = 0;
  unsigned long until;

  // TODO why is 15 apparently working, but not 0? fet / measurement?

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

      // turn on the fet with the current index (as-if to shock that channel)
      Serial.print("fet ");
      Serial.print(c_fet);
      msk::start_shock(c_fet);
      // why does the whole exchange take so long? is it really taking a few
      // seconds to print stuff? other calls?
      // TODO if it is averaging ~1353 readings in per_fet_ms
      // why does the whole exchange take so long? is it really taking a few
      // seconds to print stuff? other calls?

      reading_count = 0;
      until = millis() + per_fet_ms;
      while (millis() <= until) {
        measurement_sum += analogRead(msk::current_signal);
        reading_count++;
      }
      // TODO it looks like there might be channel specific offset?
      // zero this in software setup in advance?

      // turn it back off
      msk::stop_shock(c_fet);

      Serial.print(": average of ");
      Serial.print(reading_count);
      Serial.print(" readings: ");
      Serial.println(((double) measurement_sum) / reading_count);
    }
    Serial.println("");
  }
}
