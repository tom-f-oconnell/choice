
// TODO set jumper between the isolated 5v and the hv_+ connection
// this will make it so switching the FETs should generate voltage over each
// measurement resistor

// TODO instructions for bypassing instr/iso amps for test purposes

// this define should reconfigure the library to allow calling some extra
// functions, including select_input_channel
#define EXPOSE_TESTING_FUNCS 1
#include <multishock.hpp>

// hacky, to get methods that otherwise we would not have access to, for testing
// purposes.
// **DO NOT** include this .cpp in any code to run experiments or collect data.
//#include "multishock.cpp"

// TODO actually, why wasn't above working? it should have been able to find
// this, unless it was 1) ignoring files w/ non .h/.hpp extensions or 2)
// moving files to some temporary directory, and not moving the .cpp file?
// maybe alternatives.

void setup() {
  Serial.begin(9600);
  msk::init();
  pinMode(LED_BUILTIN, OUTPUT);

  // TODO need to throw away any analogReads?
}

void loop() {
  const unsigned int per_channel_ms = 5000;
  // play around with?
  const unsigned int per_fet_ms = 150;
  unsigned int measurement;

  // TODO sequentially try measureing all channels, toggling all channels
  // and then toggling only the particular channel, or maybe all?

  // TODO maybe try toggling all, as that code may be harder to screw up
  // than bit shifting for individual channels

  for (unsigned char c_measure=0; c_measure<msk::num_channels; c_measure++) {
    Serial.print("selecting channel ");
    Serial.print(c_measure);
    Serial.println(" to measure");
    msk::select_input_channel((msk::channel_t) c_measure);

    // try switching each shock delivery MOSFET, one at a time
    // and measure the output of the multiplexers
    for (unsigned char c_fet=0; c_fet<msk::num_channels; c_fet++) {
      // TODO average the values during this period?
      // might be easier to take a fixed number of measurements, in that case
      measurement = analogRead(msk::current_signal);
      Serial.println(measurement);
      // TODO or just loop, taking measurements until per_fet_ms has elapsed?
      delay(per_fet_ms);
    }
    delay(per_channel_ms);
  }

}
