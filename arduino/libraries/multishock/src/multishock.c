/*
 * multishock.h - Wiring/Arduino library to control shock delivery and 
 * measurement board. Can deliver up to 150v to 16 channels, and measure 
 * current through each of them.
 *
 * Connections:
 * -three optoisolators connected to pins 4-9 for digital inputs
 * -isolation amplifier output to pin A0
 * -5v pin (output of Arduino's linear regulator / (direct?) USB) to create an 
 *  isolated power supply
 *
 * Circuit features:
 * -galvanically isolated (assuming high voltage power supply is itself isolated)
 *
 * Created January 2018
 * Author: Tom O'Connell
 * Hong Lab @ Caltech
 * http://www.ejhonglab.org
 *
 * https://github.com/tom-f-oconnell/choice for schematic (in 
 * design/pcb/shield_pcb), and supporting files
 */

#include "multishock.h"
// TODO need to include Arduino stuff here as well?

// TODO
// is there some way to indicate which compile time #define flags are available
// without commenting them out like this?
//#define BYPASS_ISOLATION

#ifdef BYPASS_ISOLATION
// TODO check. be careful here...
// TODO TODO relies on only using HIGH and LOW for digital write...
// maybe use some macro based solution?
#undef HIGH
#undef LOW
#define HIGH 0
#define LOW  1
#endif

#define NUM_SHIFT_REGISTERS 3
#define NUM_CHANNELS 16

static unsigned char reg_bits[NUM_SHIFT_REGISTERS];

// TODO i think i want a bit vector of 0/1 with each being whether the channel
// with that index is being shocked? conversion functions
// or do i only want to convert to bit vector just before moving to shift regs?

// to facilitate cycling between channels for measurement. better way?
static chamber_num_t to_measure[NUM_CHANNELS];
static unsigned char curr_channel_index;

void ms_init() {
	// TODO maybe check if we are using certain boardtypes w/ Arduino
	// defines to use port manipulation optimizations?
	pinMode(SER, OUTPUT);
	pinMode(SRCLK, OUTPUT);
	pinMode(SRCLR, OUTPUT);
	pinMode(RCLK, OUTPUT);
	pinMode(FET_ENBL, OUTPUT);
	pinMode(DEMUX_ENBL, OUTPUT);

	// TODO make a wrapper function that sets a pin to output and sets initial 
	// state? maybe a macro? (would make sure all initial states are software
	// defined)

	// TODO maybe include bypass isolation option
	// TODO TODO should the circuit be designed such that all inputs low is a valid 
	// initial state? (probably w/ inverters and such)
	digitalWrite(SER, HIGH);
	digitalWrite(SRCLK, HIGH);
	// sending this s.r. pin LOW clears the bits
	digitalWrite(SRCLR, LOW);
	digitalWrite(RCLK, HIGH);

	// LOW on output enable enables the shift register
	// and the isolation inverts the logic
	digitalWrite(FET_ENBL, HIGH);
	digitalWrite(DEMUX_ENBL, HIGH);

	for (int i=0; i<NUM_SHIFT_REGISTERS; i++) {
		reg_bits[i] = 0;
	}
}

void ms_start_shock(chamber_num_t chamber_num) {
	// TODO worth using custom chamber_num type if i need to cast here?
	// do i need to cast? worries about going from signed to unsigned, etc?
	
}

void ms_stop_shock(chamber_num_t chamber_num) {
	
}

measurement_t ms_measure(chamber_num_t chamber_num) {

}

// TODO below / above / both? both, but prohibit mixing somehow?
// maybe compile time flag to pick one?

// TODO need to decide whether to check (double adding would be bad)
void ms_queue_measurement(chamber_num_t chamber_num) {

}

// ms_measure_next? is this overloading? supported?
chamber_measurement ms_measure() {

}

// TODO i need at least 3 8 bit bytes of state to remember current register
// states. and i'm assuming i'll need to do that to modify only part, right?

// TODO would it make the most sense to use a class to store queue of chambers
// to measure from? other way of maintaining state? leave to user to cycle?

// TODO worth packing together 10 bit analogRead return and only sending multiple 
// at once? see Ben Krasnow's "ping-pong" buffer code?
// or maybe lesser # of bits for faster acquisition, and then it might make more sense?

// TODO best order of function definitions in c/cpp? dependencies first, 
// or high level up top?
// TODO include option to compile without delay? is there some way libraries
// allow compile time configuration?
void clear_reg() {
	// TODO consistent indentation. guidelines on in-function preprocessor 
	// conditionals like these (re: formatting)?
    digitalWrite(SRCLR, HIGH);
    digitalWrite(RCLK, HIGH);
#ifndef SR_NODELAY
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, LOW);
#ifndef SR_NODELAY
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, HIGH);
    digitalWrite(SRCLR, LOW);
#ifndef SR_NODELAY
    delay(SHIFTREG_PERIOD_MS);
#endif
  }
}

// takes HIGH (1) or LOW (0) as input
void shift_in(unsigned char value) {
  // logic should be inverted IF USING optoisolator
  // TODO if i'm not passing BYPASS_ISOLATION, maybe just use preprocessor conditional?
    digitalWrite(SRCLK, HIGH);
#ifndef SR_NODELAY
  delay(SHIFTREG_PERIOD_MS);
#endif
  
    // TODO TODO currently handling of bypass_isolation breaks here. fix.
    digitalWrite(SER, 1 - value);
#ifndef SR_NODELAY
  delay(SHIFTREG_PERIOD_MS);
#endif
  
    digitalWrite(SRCLK, LOW);
#ifndef SR_NODELAY
  delay(SHIFTREG_PERIOD_MS);
#endif
}

void update_output() {
    digitalWrite(RCLK, HIGH);
#ifndef SR_NODELAY
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, LOW);
#ifndef SR_NODELAY
    delay(SHIFTREG_PERIOD_MS);
#endif
}

// TODO store side information as another bit in a uchar / decode
// c should be between 0 and 7
// TODO should channel get a type different from chamber_num_t?
void select_input_channel(boolean left_side, unsigned char c) {
  // need to shift in starting with last value (QD; optional_demux_enable)
  // optional_demux_enable -> chan_select_B -> chan_select_A ->
  // demux_select_B -> demux_select_A
  clear_reg();
  
  // will always want to enable analog switch output
  shift_in(0);

  // "channels" are numbered from 1 to 8, so odd numbers come first
  // B (on CD4052B): 0 -> 0/1 (odd channels), 1 -> 2/3 (even channels)
  // TODO check this
  shift_in(1 - c % 2);
  
  // A (on CD4052B): 0 -> lower numbered choice given B (LEFT by my def), 1 -> higher (RIGHT)
  if (left_side) {
    shift_in(1);
  } else {
    shift_in(0);
  }

  // CD4556 (B): 0 -> Q0/Q1 (channels 1-2/3-4), 1 -> Q2/Q3 (channels 5-6/7-8)
  shift_in(c > 4);

  // CD4556 (A): 0 -> lower of above, 1 -> higher
  // TODO replace w/ one bitwise operation (at least verify)
  shift_in(c == 3 || c == 4 || c == 7 || c == 8);

  update_output();
}

#endif
