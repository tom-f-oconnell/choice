/*
 * TODO connections for leds for enable + each select pin
 * and also for each demux, to test 4556
 */

#include <multishock.hpp>

void setup() {
  Serial.begin(9600);
  msk::init();
}

// TODO where should I test the consequences of enable pin on whether / which
// channel is being measured? here?

// TODO paste chip truth tables in here + expected combinations of bits per
// channel

// TODO as-is, addressing of u4 and u5 (with numbering defined to be correct for
// FETs) is swapped. fix

// TODO share in some helper thing? put in library?
void print_bits(uint8_t bitvector) {
  int group = 0;
  // only care about the first 5 bits
  // printing more to determine appropriate masks and stuff
  for (char i=7; i >= 0; i--) {
  //for (char i=0; i < 8; i++) {
    Serial.print((bitvector >> i) & 1);
    group++;
    if (group == 4) {
      Serial.print(" ");
      group = 0;
    }
  }
  Serial.println("");
}

void loop() {
  const unsigned int per_channel_ms = 10000;
  unsigned char chip;
  unsigned char last_chip = -1;

  for (unsigned char c_measure=0; c_measure<msk::num_channels; c_measure++) {

    if (c_measure <= 3) {
      // 1+/- through 4+/- (channels in schematic numbered from 1, here from 0)
      chip = 3;

    } else if (c_measure > 3 && c_measure <= 7) {
      chip = 4;

    } else if (c_measure > 7 && c_measure <= 11) {
      chip = 5;

    } else if (c_measure > 11 && c_measure <= 15) {
      chip = 6;

    } else {
      // should be unreachable. maybe print a warning.
    }

    if (chip != last_chip) {
      Serial.print("INH should only be LOW on CD4052 U");
      Serial.println(chip);
      last_chip = chip;
    }

    Serial.print("demux channel ");
    Serial.print(c_measure);
    Serial.print(" ");

    msk::_select_input_channel(c_measure);

    // want the state after selecting the channel
    // the above function edits these bits
    print_bits(msk::_get_demux_states());
    delay(per_channel_ms);
  }
}

