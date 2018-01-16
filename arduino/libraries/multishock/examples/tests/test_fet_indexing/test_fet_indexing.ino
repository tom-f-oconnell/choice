/* 
 * Connections:
 * 1) For each channel, connect a 100 ohm resistor to a through-hole LED. You
 *    can do this either by twisting one of each of their legs together, or
 *    soldering.
 * 2) Put the side of the LED that should be attached to positive voltage into
 *    the terminal of the MOSFET socket that would connect to its gate, and
 *    ground the other leg of the resistor / LED pair in the grounded terminal
 *    of the socket.
 * 3) Repeat for each MOSFET socket.
 *
 * Success:
 *
 *
 * TODO specify which these are in the boards with the MOSFET pinswap fixed
 *
 * Errors: Any demux bits are high. could only check with more prep though TODO
 *
 * TODO if they were high before upload, and no reset? voltatile? before power
 * cycle? (test both if possible)
 *
 */

// TODO try to figure out what is causing some of the bits (maybe just demux?)
// to go high (during init? reset?)

// this define should reconfigure the library to allow calling some extra
// functions, including select_input_channel
#include <multishock.hpp>

// comment to compile without printing fet_states
#define PRINT_FET_STATES

void print_bits(uint16_t bitvector) {
  int group = 0;
  for (unsigned char i=0; i<16; i++) {
    Serial.print((bitvector >> i) & 1);
    group++;
    if (group == 4) {
      Serial.print(" ");
      group = 0;
    }
  }
  Serial.println("");
}

void setup() {
  Serial.begin(9600);
  // TODO time
  msk::init();
  pinMode(LED_BUILTIN, OUTPUT);

  // TODO explicit clear_reg first?

  #ifdef PRINT_FET_STATES
    Serial.println("initial fet_states:");
    print_bits(msk::_get_fet_states());
  #endif
}

void loop() {
  const unsigned int per_channel_ms = 400;

  // try switching each shock delivery MOSFET, one at a time
  // and measure the output of the multiplexers
  for (unsigned char c_fet=0; c_fet<msk::num_channels; c_fet++) {
    Serial.print("fet ");
    Serial.println(c_fet);

    // turn on the fet with the current index (as-if to shock that channel)
    // TODO time
    msk::start_shock(c_fet);
    #ifdef PRINT_FET_STATES
      Serial.println("on");
      print_bits(msk::_get_fet_states());
    #else
      Serial.print(" on");
    #endif

    delay(per_channel_ms);

    // turn it back off
    // TODO time
    msk::stop_shock(c_fet);
    #ifdef PRINT_FET_STATES
      Serial.println("off");
      print_bits(msk::_get_fet_states());
    #else
      Serial.println(" off");
    #endif
  }
}
