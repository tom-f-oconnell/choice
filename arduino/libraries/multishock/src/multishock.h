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
 * TODO maybe move this section to a pcb design readme or something?
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

// TODO underscores / idiomatic capitalization?
#ifndef SHOCK_H
#define SHOCK_H

// TODO maybe include that wprogram bit
//
// TODO could also use the below, if feeling ambitious
// #if defined(ARDUINO_ARCH_AVR)
// #elif defined(ARDUINO_ARCH_SAM)
// which SAM boards are there I might want to support?
// just notify people it likely won't work with those if I end up using 
// lower level features?
// #endif

// TODO could also
// #else
//   # error "This library only supports boards with an AVR or SAM processor."
// #endif

/*
* Pins to control three 74HC595 shift registers, all daisy chained together.
*
* Each shift register has 8 independent output pins.
*
* The first two control 8 MOSFETs each, which administer shocks.
*
* The first five pins of the third are, in order:
* Input A and B to a CD4556B, input A and B to ALL FOUR CD4052Bs (the analog
* demultiplexers), and the E(nable) pin on the 4556.
*
* These first two inputs define which CD4052B is active, the 4052 shared 
* inputs select which channel of the active 4052 is used, and the final enable
* pin can be used to disable all of the 4052s.
*
* The remaining 3 pins on the third shift register are not used.
*
* TODO include truth tables of 4556 and 4052? operation of 74HC595?
* or maybe just a reference to page of datasheet for the last one?
*
*/
// TODO maybe actually avoid defines, or prefix to prevent possible conflicts?
#define SER   4
#define SRCLK 5
#define SRCLR 6
#define RCLK  7
#define FET_ENBL   8
#define DEMUX_ENBL 9 

// the input from the isolation amplifier
// should be proportional to the current the fly received (on whichever 
// demultiplexer channels is currently selected), within the working range
#define CURRENT_SIGNAL A0

//#define SHIFT_REGISTER_BITS 21
#define SHIFTREG_PERIOD_MS 50

// TODO how were these used differently?
//#define MIN_DEMUX_PERIOD_MS 1
#define PERIOD_PER_CHANNEL_MS 5000
//#define FET_SWITCH_TO_SAMPLE_MS 1

// TODO to what extent / should i use namespaces? for things like constants?
// functions? (vs. prefix?)

// TODO typedef chamber_num and measurement type, to make it easier to change
// if i did happen to want to?
// TODO organize typdefs all at top, or just above their use?
typedef unsigned char chamber_num_t;
typedef unsigned int measurement_t;

typedef struct {
	chamber_num_t chamber_num;
	measurement_t measurement;
} chamber_measurement;
// TODO capitalization above? style?

void ms_init();

// caller will be responsible for ensuring the chamber_num is valid
// (could return int if invalid... probably don't want to though)
void ms_start_shock(chamber_num_t chamber_num);
void ms_stop_shock(chamber_num_t chamber_num);

measurement_t ms_measure(chamber_num_t chamber_num);

// TODO below / above / both? both, but prohibit mixing somehow?

// TODO need to decide whether to check (double adding would be bad)
void ms_queue_measurement(chamber_num_t chamber_num);
// ms_measure_next?
chamber_measurement ms_measure();

// TODO i need at least 3 8 bit bytes of state to remember current register
// states. and i'm assuming i'll need to do that to modify only part, right?

// TODO would it make the most sense to use a class to store queue of chambers
// to measure from? other way of maintaining state? leave to user to cycle?

// TODO worth packing together 10 bit analogRead return and only sending multiple 
// at once? see Ben Krasnow's "ping-pong" buffer code?
// or maybe lesser # of bits for faster acquisition, and then it might make more sense?


#endif
