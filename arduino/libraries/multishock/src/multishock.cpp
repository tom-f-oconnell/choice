/*
 * multishock.cpp - Wiring/Arduino library to control shock delivery and 
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

// TODO unit tests, off any microcontroller

// maybe get rid of this, if it interferes w/ compilation outside of Arduino IDE?
// maybe just check that alternate flags are NOT set?
#ifndef ARDUINO_ARCH_AVR
  # error "This library only currently supports boards with an AVR processor."
#endif

// maybe don't check if ARDUINO is defined, for compilation outside IDE?
// (default to one of the headers?)
#if defined(ARDUINO)
#if ARDUINO >= 100
    #include <Arduino.h>  // Arduino 1.0
#else
    #include <WProgram.h> // Arduino 0022
#endif

#else
    #error "Using Arduino functions but "\
    "not compiling in an Arduino environment."
#endif

#include "multishock.hpp"

namespace msk {
    // TODO
    // is there some way to indicate which compile time #define flags are available
    // without commenting them out like this?
    //#define BYPASS_ISOLATION

    /*
    #ifdef BYPASS_ISOLATION
    // TODO check. be careful here...
    // TODO TODO relies on only using HIGH and LOW for digital write...
    // maybe use some macro based solution?
    #undef HIGH
    #undef LOW
    #define HIGH 0
    #define LOW  1
    #endif
    */

    // from arduino.cc:
    // ints are 16 bits on ATmega based boards, but 32 on Due / SAMD / maybe others
    // TODO maybe handle differently? not sure what would stop someone from compiling
    // on Due for now, if still AVR? **explicitly use 16bit type?**
    // maybe just make one macro to repeat 8 times? (n times seems harder / 
    // impossible? w/o boost preprocessor lib?)
    // TODO maybe use uintN_t just to be clear on sizes (that is what is important)
    // TODO maybe don't rely on 
    // TODO maybe define in init, checking odd?
    typedef unsigned int fet_mask_t;
    static const fet_mask_t all_fets  = 0b1111111111111111;
    static const fet_mask_t no_fets   = 0;
    static const fet_mask_t all_left  = 0b0101010101010101;
    static const fet_mask_t all_right = 0b1010101010101010;

    //#define SET(x,n) x |= (1 << n)
    //#define CLEAR(x,n) x &= ~(1 << n)
    //#define READ(x,n) ()

    // could i use this to define masks compile time? (prob not, but maybe)
    // number of bits used in each bank of shift registers
    // with bank of two fet registers preceeding the single demux reg
    static const unsigned char fet_bits = 16;
    static const unsigned char demux_bits = 5;
    // TODO TODO include constants to help understanding purpose of each demux_bit
    static const unsigned char lowest_demux_state_bit = 1;
    static const unsigned char demux_enable_bit = 0;

    // TODO compile time assert that measurement_bits + channel_bits is less than
    // sizeof(channel_measurement_t) * 8?

    // 16 bits
    static fet_mask_t fet_states;
    // 8 bits, the rightmost (? TODO) 5 of which are used
    static unsigned char demux_states;

    // wanted to also use this to defined sizes of masks, 
    // but it proved difficult
    static unsigned char num_channels = 16;
    // TODO could do as a mask? (same size as fet_mask_t)
    // to facilitate cycling between channels for measurement. better way?
    static channel_t to_measure[num_channels];
    // this line requires channel_t to be at least 8 bits (more if signed)
    // TODO -1 work without this limitation?
    static const channel_t no_channel = 255;
    static unsigned char curr_channel_index;
    static unsigned char next_free_index;

    // TODO should i declare all of the other functions static? does it matter?
    // (as long as they aren't in the header?)

    // TODO worth packing together 10 bit analogRead return and only sending multiple 
    // at once? see Ben Krasnow's "ping-pong" buffer code?
    // or maybe lesser # of bits for faster acquisition, and then it might make more sense?

    // TODO  is there some way libraries allow compile time configuration?
    static inline void clear_reg() {
        // TODO consistent indentation. guidelines on in-function preprocessor 
        // conditionals like these (re: formatting)?
        digitalWrite(srclr, HIGH);
        digitalWrite(rclk, HIGH);

        // TODO replace SR_NODELAY stuff w/ something like macro condensing both 
        // calls?
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
        digitalWrite(rclk, LOW);
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
        digitalWrite(rclk, HIGH);
        digitalWrite(srclr, LOW);
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
      }
    }

    static inline void update_output() {
        digitalWrite(rclk, HIGH);
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
        digitalWrite(rclk, LOW);
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
    }

    // TODO if only really supporting a few AVR boards anyway, maybe just
    // look up the relevant port manipulations to get rid of digitalWrites

    // TODO TODO consider grouping pins on shield st port manipulations can switch
    // pins that generally / always change state together at the same time

    // takes HIGH (1) or LOW (0) as input (w/ way i had started implementing 
    // BYPASS_ISOLATION, this would not necessarily be the case)
    static inline void shift(unsigned char bit) {
        // logic should be inverted IF USING optoisolator
        digitalWrite(srclk, HIGH);
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
      
        // TODO TODO currently handling of bypass_isolation breaks here. fix.
        // TODO might prefer to treat in a way where the default execution
        // does not require the negation (using inverting optoisolators). how?
        digitalWrite(ser, !bit);
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
      
        digitalWrite(srclk, LOW);
        #ifndef SR_NODELAY
            delay(shiftreg_period_ms);
        #endif
    }

    // TODO way to warn if something can not be inlined?
    // (so i could switch to macros, etc)

    // TODO i might like to have a shift_out(mask, n_bits), but seems it 
    // would be hard for a compiler to inline? maybe not? (const n_bits)
    // TODO some other style that would not require hidden state?
    // (explicitly passing masks)
    // TODO TODO gcc loop unrolling directive / test it
    // https://stackoverflow.com/questions/4071690/\
    // tell-gcc-to-specifically-unroll-a-loop

    /* Update shift register bits to match [fet/demux]_states and make the
     * register outputs reflect the inputs they just received.
     *
     * Should (replace with "Does" after checking) not enable or disable output.
     */
    static inline void update_registers() {
        // shift all bits to registers ***in reverse order*** (well... demux...)
        // TODO actually... check this order is correct. especially for demux flags.
        // if forward order is more readily unrolled, store state in reverse?
        for (unsigned char i=0; i<demux_bits; i++) {
            shift((demux_states >> i) & 1);
        }

        // TODO TODO > 0 or >= 0? test!!
        for (unsigned char i = (fet_bits - 1); i >= 0; fet_bits; i--) {
            // TODO i assume using more space (8 bit type per channel)
            // would make this part faster? at expense of maybe setting bits in
            // local variable slower? (even out?)
            // TODO 1 is uchar?
            shift((fet_states >> i) & 1);
        }

        // assuming, for now, that there are no cases where I'd shift in new
        // bits, without immediately wanting to update the output
        // (enable controlled separately (right?))
        update_output();
    }

    static inline void select_input_channel(channel_t channel) {
        // need to shift in starting with last value (QD; optional_demux_enable)
        // optional_demux_enable -> chan_select_B -> chan_select_A ->
        // demux_select_B -> demux_select_A

        // TODO make sure order in here is correct...
        // related to other note, maybe pick order that allows forward shifting
        
        // will always want to enable analog switch output
        // TODO true? compile options for this / enable each time / enable when
        // anything in queue?
        // TODO if demux enable if is MSB (and all 5 bits are LS of this byte)
        // is that order consistent w/ fet_states? maybe just redefine those,
        // and numbering, as long as demux_enable goes in right place?
        // TODO if i want to change back to forward order, demux_enable 
        // should be 0, i think
        demux_states |= 1 << demux_enable_bit;
      
        // TODO update note on numbering
        // "channels" are numbered from 1 to 8, so odd numbers come first
        // B (on CD4052B): 0 -> 0/1 (odd channels), 1 -> 2/3 (even channels)
        // TODO check this
        // TODO TODO is this trying to deal with the negation twice?
        // what was purpose of 1 - here?
        //shift(1 - c % 2);

        // TODO TODO maybe redo numbering s.t. requires minimal bitwise operations
        // to set demux_states
        // TODO i suppose if all 4(-6) bit channel numbers are valid, i could just
        // directly translate those to demux_states, and see what that numbering is?

        demux_states |= channel << lowest_demux_state_bit;

        // update values in shift registers
        // we only changed bits on last one, but they are all daisy chained.
        update_registers();
    }

    // TODO might want to move this to the top if i don't end up needing other functions
    // only declared in here
    void init() {
        // TODO maybe check if we are using certain boardtypes w/ Arduino
        // defines to use port manipulation optimizations?
        pinMode(ser, OUTPUT);
        pinMode(srclk, OUTPUT);
        pinMode(srclr, OUTPUT);
        pinMode(rclk, OUTPUT);
        pinMode(fet_enbl, OUTPUT);
        pinMode(demux_enbl, OUTPUT);

        // TODO make a wrapper function that sets a pin to output and sets initial 
        // state? maybe a macro? (would make sure all initial states are software
        // defined)

        // TODO TODO should the circuit be designed such that all inputs low is a valid 
        // initial state? (probably w/ inverters and such)
        digitalWrite(ser, HIGH);
        digitalWrite(srclk, HIGH);
        // sending this s.r. pin LOW clears the bits
        digitalWrite(srclr, LOW);
        digitalWrite(rclk, HIGH);

        // LOW on output enable enables the shift register
        // and the isolation inverts the logic
        digitalWrite(fet_enbl, HIGH);
        digitalWrite(demux_enbl, HIGH);

        // TODO TODO do SRs lose state upon reboot (for sure)? explicitly clear?
        fet_states = 0;
        demux_states = 0;

        curr_channel_index = 0;
        next_free_index = 0;
        for (unsigned char i=0;i<num_channels;i++) {
            to_measure[i] = no_channel;
        }
        // maybe define some bit pattern (effective) constants here?
        // particularly if i'm having trouble w/ binary literals
    }

    // SR pins go from F1-16 in order through first two SRs
    // in v0.1, F1=bottom right, F2=bottom left (w/ D-Sub connector of floor down)
    // ..., F16=top left

    /* TODO 
     * NOTE: Channels are numbered starting from 0 (to 15).
     */
    void start_shock(channel_t channel) {
        // get the bit that corresponds to this channel number
        // and OR in the bit for this channel number (make it a 1 if it wasn't)
        // to the bit-vector holding state of the two stimulus shift registers
        fet_states |= 1 << channel;
        
        // TODO does actually passing the parameter make things more 
        // complicated to optimize? (to shift_out) might save on code size
        // if not inlined...
        
        // shift all the bits out (from fet_states to registers) again
        // including (and starting with) the 5 measurement-related bits
        update_registers();
    }

    /* TODO 
     * NOTE: Channels are numbered starting from 0 (to 15).
     */
    void stop_shock(channel_t channel) {
        fet_states &= 0 << channel;
        update_registers();
    }

    // just assuming for now there may be cases where someone wants to actually
    // *only* stop shocking all of the left / right, but may consider removing
    // these two functions
    // TODO implement differently, to avoid combinatorial group of 6 functions?

    /* Sets bits such that (only) when the FET shift registers are enabled, ALL
     * channels will receive voltage.
     */
    void start_all_shock() {
        fet_states = all_fets;
        update_registers();
    }

    /* Sets bits such that (even) when the FET shift registers are enabled, NO
     * channels will receive voltage.
     */
    void stop_all_shock() {
        fet_states = no_fets;
        update_registers();
    }

    /* Sets bits such that (only) when the FET shift registers are enabled, 
     * AT LEAST all of the left channels will receive voltage.
     *
     * Does not change voltage at any of the right channels.
     */
    void start_shock_left() {
        fet_states |= left_fets;
        update_registers();
    }

    /* Sets bits such that (even) when the FET shift registers are enabled, the 
     * left channels will not receive voltage.
     *
     * Does not change voltage at any of the right channels.
     */
    void stop_shock_left() {
        fet_states &= right_fets;
        update_registers();
    }

    /* Sets bits such that (only) when the FET shift registers are enabled, 
     * AT LEAST all of the right channels will receive voltage.
     *
     * Does not change voltage at any of the left channels.
     */
    void start_shock_right() {
        fet_states |= right_fets;
        update_registers();
    }

    /* Sets bits such that (even) when the FET shift registers are enabled, the 
     * right channels will not receive voltage.
     *
     * Does not change voltage at any of the left channels.
     */
    void stop_shock_right() {
        fet_states &= left_fets;
        update_registers();
    }

    /* Enables output of the two shock control shift registers, using their
     * OE (output enable) pins, which are tied together on the PCB.
     *
     * Faster than the start_shock* functions.
     *
     * Does not change contents of registers.
     */
    void enable_shock() {
        // on 74HC595, OE=LOW -> output enabled, OE=HIGH -> output disabled
        // and optoisolators invert the logic
        digitalWrite(fet_enbl, HIGH);
    }

    /* Brings output of the two shock control shift registers LOW, using their
     * OE (output enable) pins, which are tied together on the PCB.
     *
     * Faster than the stop_shock* functions.
     *
     * Does not change contents of registers.
     */
    void disable_shock() {
        digitalWrite(fet_enbl, LOW);
    }

    // TODO auto-enable if measuring at all / disable if not? or do it each 
    // measurement? check 4052 datasheet for time / other penalties involved 
    // or for reasons to disable at all...
    
    /* TODO
     */
    void enable_inputs() {
        // TODO check demuxes are actually disabled when that sr is 
        // set this way
        digitalWrite(demux_enbl, HIGH);
    }

    /* TODO
     */
    void disable_inputs() {
        digitalWrite(demux_enbl, LOW);
    }

    /* Returns a measurement_t (>= measurement_bits bits in type) read
     * as soon as possible, without interacting with to_measure queue.
     * 
     * Assumes inputs are already enabled. (?)
     */
    measurement_t measure(channel_t channel) {
        measurement_t measurement;
        measurement = analogRead(current_signal);
        return measurement;
    }

    // TODO consider returning channel_measurement_t type regardless
    // or offering both. might depend on whether processing responses
    // in real time (w/ host sending channel nums)
    /* (like this)
    channel_measurement_t measure(channel_t channel) {
        channel_measurement_t ret;
        // TODO need to set to zero? just a waste of a cycle?
        ret |= channel << 

    }
    */

    // TODO below / above / both? both, but prohibit mixing somehow?
    // maybe compile time flag to pick one?

    /* Returns 1 (which evaluates true) if channel is already queued to be 
     * measured. Returns 0 (which evaluates false), otherwise.
     */
    unsigned char will_be_measured(channel_t channel) {
        // TODO unit test
        // TODO maybe get rid of these ugly premature optimizations
        channel_t c;
        // could maybe get smaller overall code by making another function
        // that returns index, and then wrapping it here, just returning if 
        // index in range. then, could use index find in stop_measurement too.
        for (unsigned char i=0;i<num_channels;i++) {
            c = to_measure[i];
            if (c == no_channel) {
                return 0;
            } else if (c == channel) {
                return 1;
            }
        }
        return 0;
    }

    // TODO change language back to queue / dequeue? or similar
    // (so it is clear measurement isn't happening upon this call)

    /* Adds channel to channels being measured. See measure() documentation.
     *
     * If CHECK_Q_DUPLICATES is true, and channel is already in to_measure,
     * this function will return without taking any action. Will not change
     * priority of that channel in the queue.
     *
     * If compiled without forcing the check, you can manually check
     * will_be_measured(channel) first, and then decide to queue.
     */
    void start_measurement(channel_t channel) {
        // TODO unit test
        // TODO maybe change flag to FORCE_/ALWAYS_...?
        #ifdef CHECK_Q_DUPLICATES
            if (will_be_measured(channel)) {
                return;
            }
            // TODO or is it more important to check next_free_index < num_channels?
        #endif
        to_measure[next_free_index] = channel;
        next_free_index++;
    }

    /* Removes channel from channels to being measured.
     * See measure() documentation.
     */
    void stop_measurement(channel_t channel) {
        unsigned char i;
        channel_t c;
        // find the current index of channel (if it exists)
        for (i=0;i<num_channels;i++) {
            // TODO unit test. bounds, not there, etc
            c = to_measure[i];
            if (c == channel) {
                // i = index of element we want to remove
                break;
            } else if (c == no_channel) {
                return;
            }
        }
        
        // TODO maybe circularly shift / something to prevent some from getting
        // read more than others if there are lots of deletes
        // TODO think more seriously about whether that could happen / 
        // do some tests to see if it does. unit test?

        // move other channels, all the way to the end of the array,
        // left to fill this position
        while (i < (num_channels - 1)) {
            to_measure[i] = to_measure[i+1];
            i++;
        }
        // TODO unit test
        // handle last element, if we to_measure was previously full
        // (we were trying to measure all of the channels)
        if (i == (num_channels - 1)) {
            to_measure[i] = no_channel;
        }
        next_free_index--;
    }

    /* Measures current correlate on next channel.
     *
     * The next channel is to_measure[curr_channel_index]. The channel index
     * is incremented, wrapping around if the next channel would be the
     * constant "no_channel".
     *
     * Returns channel and measurement as one (16 bit) numeric type.
     * Channel should be leftmost 6 bits and measurement should be rightmost 10.
     * See "channel_bits" and "measurement_bits" in "multishock.hpp".
     */
    channel_measurement_t measure() {
        // TODO need to explicitly zero this first?
        channel_measurement_t channel_measurement;
        measurement_t measurement;
        channel_t channel = to_measure[curr_channel_index];

        // switch the analog demultiplexers to the channel
        // TODO and enable them? do i ever want to disable them?
        select_input_channel(channel);

        // TODO directly call AVR functions?
        measurement = analogRead(current_signal);

        // shift channel up to it's position in the bits of the number
        // to be returned, and OR it in
        channel_measurement |= channel << measurement_bits;

        // If >10 bits, and you had not made other modifications to accomodate
        // that, you could shift measurement right two bits to get 10 most
        // significant bits.
        
        // OR in measurement bits. assuming it is 10 bits for now.
        // TODO check will only compile on Arduino's w/ 10 bit ADCs
        // or warn and force setting ADC resolution to 10 bits / truncate
        channel_measurement |= measurement;

        // increment current channel index, to measure another channel on the
        // next call to this function
        // TODO maybe replace curr_channel_index w/ channel_index?
        curr_channel_index++;
        // TODO unit test
        if (curr_channel_index >= num_channels || \
            to_measure[curr_channel_index] == no_channel) {

            curr_channel_index = 0;
        }
        return channel_measurement;
    }

    // TODO is it worth a "measure_all" function?
    // return type might be more complicated...
}
#endif
