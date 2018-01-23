/*
 * multishock.cpp - C++/Arduino library to control shock delivery and 
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
 * -galvanically isolated (assuming high voltage power supply is itself
 *  isolated)
 *
 * Created January 2018
 * Author: Tom O'Connell
 * Hong Lab @ Caltech
 * http://www.ejhonglab.org
 *
 * https://github.com/tom-f-oconnell/choice for schematic (in 
 * design/pcb/shield_pcb), and supporting files
 */

// maybe don't check if ARDUINO is defined, for compilation outside IDE?
// (default to one of the headers?)
#if defined(ARDUINO)
// maybe get rid of this, if it interferes w/ compilation outside of Arduino
// IDE?
// maybe just check that alternate flags are NOT set?
#ifndef ARDUINO_ARCH_AVR
  # error "This library only currently supports boards with an AVR processor."
#endif

#if ARDUINO >= 100
    #include <Arduino.h>  // Arduino 1.0
#else
    #include <WProgram.h> // Arduino 0022
#endif

// TODO I think I want to include GNU stdint.h if just want those types for
// unit tests, since I'm not testing the stuff involving Arduino hardware calls
// but, I am not sure how to break up the code, s.t. hardware stuff is separate
// (to avoid compilation problems compiling w/o Arduino functions)
// TODO but i probably should break up the code?
#elif defined(UNIT_TESTING)
// TODO how to find / get this in a portable way?
// want this for the fixed bit-length types
#include <stdint.h>

// TODO delete me
#include <iostream>
#include <bitset>

/*
#include <limits.h>
#define str_helper(x) #x
#define str(x) str_helper(x)
#pragma message str(UINT_MAX)
#pragma message str(INT_MAX)
*/

#else
    #error "Using Arduino functions but not compiling in Arduino environment."
#endif

#include "multishock.hpp"

#define SR_NODELAY

namespace msk {
    // TODO is there some way to indicate which compile time #define flags are
    // available without commenting them out like this?
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

    // TODO maybe change types to "fastest?" / related?
    typedef uint16_t fet_mask_t;
    // TODO maybe define in init, checking odd?
    // TODO maybe switch to 0x notation (C standard?) as 0b is only definitely
    // supported in GCC
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
    static const uint8_t fet_bits = 16;
    static const uint8_t demux_bits = 5;
    // TODO include constants to help understanding purpose of each demux_bit
    static const uint8_t lowest_demux_state_bit = 0;
    // TODO define demux_enabled to 0? (want it so output of _get_demux_enable()
    // is testable against the (potentially redefinable) constant, but also
    // don't know if i want to expose the constant in the header...
    // TODO test in separate set of tests w/ access to static variables?
    // TODO way to couple EDA schematic and driver more tightly? like
    // autogenerate bits for certain labels of same name?
    static const uint8_t demux_select_A_bit = 0;
    static const uint8_t demux_select_B_bit = 1;
    static const uint8_t chan_select_A_bit = 2;
    static const uint8_t chan_select_B_bit = 3;
    static const uint8_t demux_enable_bit = 4;
    static const uint8_t demux_enabled = 0;

    // TODO maybe get rid of? maybe hoist to header if i can't get rid of need
    // for _get_<states> calls?
    // 16 bits
    static fet_mask_t fet_states;
    // 8 bits, the rightmost (? TODO) 5 of which are used
    static uint8_t demux_states;

    // TODO could do as a mask? (same size as fet_mask_t)
    // to facilitate cycling between channels for measurement. better way?
    static channel_t to_measure[num_channels];
    static uint8_t curr_channel_index;
    static uint8_t next_free_index;

    // TODO should i declare all of the other functions static? does it matter?
    // (as long as they aren't in the header?)

    // TODO worth packing together 10 bit analogRead return and only sending
    // multiple at once? see Ben Krasnow's "ping-pong" buffer code?
    // or maybe lesser # of bits for faster acquisition, and then it might make
    // more sense?

    // all functions that depend on Arduino libraries (which I generally would
    // not want to unit test anyway) grouped for exclusion from unit test
    // compilation. to compile unit tests without having arduino libraries.
    #ifdef ARDUINO
        // TODO TODO TODO make sure "disabling" the shift registers (which
        // should put the pins in a HIGH IMPEDANCE state) works to keep all FETs
        // off, and the demultiplexers in the most harmless or lowest power
        // consumption state possible
        // TODO if it does not in one case (especially FET), can not just toggle
        // enable to get faster switching. will need to rethink
        
        // TODO inline all of these pin setting functions as well?

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

        /* Brings output of the two shock control shift registers LOW, using
         * their OE (output enable) pins, which are tied together on the PCB.
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
            digitalWrite(demux_enbl, HIGH);
        }

        /* TODO
         */
        void disable_inputs() {
            // TODO check demuxes are actually disabled when that sr is 
            // set this way
            digitalWrite(demux_enbl, LOW);
        }

        // TODO  is there some way libraries allow compile time configuration?
        
        // TODO test all commands to shift register in mixed mode simulator, if
        // i get the time
        // TODO or try out ArduinoUnit or something like that + test rig maybe
        // on a permanent hardware test unit

        inline void _clear_reg() {
            // TODO consistent indentation. guidelines on in-function
            // preprocessor conditionals like these (re: formatting)?
            digitalWrite(srclr, HIGH);
            digitalWrite(rclk, HIGH);

            // TODO replace SR_NODELAY stuff w/ something like macro condensing
            // both calls?
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

        inline void _update_output() {
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

        // TODO TODO consider grouping pins on shield st port manipulations can
        // switch pins that generally / always change state together at the same
        // time

        // takes HIGH (1) or LOW (0) as input (w/ way i had started implementing
        // BYPASS_ISOLATION, this would not necessarily be the case)
        inline void _shift(uint8_t bit) {
            // logic should be inverted IF USING optoisolator
            digitalWrite(srclk, HIGH);
            #ifndef SR_NODELAY
                delay(shiftreg_period_ms);
            #endif
          
            // TODO TODO currently handling of bypass_isolation breaks here. fix
            // TODO might prefer to treat in a way where the default execution
            // does not require the negation (using inverting optoisolators).
            // how?
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
        // https://stackoverflow.com/questions/4071690/
        // tell-gcc-to-specifically-unroll-a-loop

        // TODO i feel like maybe I could have tested this if I had some way to
        // mock shift?
        // TODO integration test
        /* Update shift register bits to match [fet/demux]_states and make the
         * register outputs reflect the inputs they just received.
         *
         * Should (replace with "Does" after checking) not enable or disable
         * output.
         */
        static inline void update_registers() {
            // TODO after other considerations, try to get it so they are
            // shifted out in same order, for easier understanding of the states
            // during debugging (if just printing w/ same function)

            for (int8_t i = (demux_bits - 1); i >= 0; i--) {
                _shift((demux_states >> i) & 1);
            }

            for (int8_t i = (fet_bits - 1); i >= 0; i--) {
                // TODO i assume using more space (8 bit type per channel)
                // would make this part faster? at expense of maybe setting bits
                // in local variable slower? (even out?)
                // TODO 1 is uchar? what about when compiled w/ avr-gcc w/ 8-bit
                // target?
                _shift((fet_states >> i) & 1);
            }

            // assuming, for now, that there are no cases where I'd shift in new
            // bits, without immediately wanting to update the output
            // (enable controlled separately (right?))
            _update_output();
        }
    #endif

    /* Takes a 4-bit channel number (in an 8-bit type, at least on 8-bit AVRs),
     * sets the variable demux_states appropriately, and then shifts this
     * variable and the fet_states back to the registers to put all of the
     * demux select lines in the correct states to select the desired input 
     * channel.
     */
    inline void _select_input_channel(channel_t channel) {
        // TODO this note still accurate? might be better placed in
        // update_registers, even if so
        // need to shift in starting with last value (QD; optional_demux_enable)
        // optional_demux_enable -> chan_select_B -> chan_select_A ->
        // demux_select_B -> demux_select_A

        // TODO maybe pick order that allows forward shifting
        
        // will always want to enable analog switch output
        // TODO true? compile options for this / enable each time / enable when
        // anything in queue?
        // TODO if demux enable if is MSB (and all 5 bits are LS of this byte)
        // is that order consistent w/ fet_states? maybe just redefine those,
        // and numbering, as long as demux_enable goes in right place?
   
        // TODO maybe move this note up top or delete
        // demux_enabled 0 because CD4556 is enabled when this pin is low
        demux_states = ((uint8_t) demux_enabled) << demux_enable_bit;
      
        // TODO update note on numbering
        // "channels" are numbered from 1 to 8, so odd numbers come first
        // B (on CD4052B): 0 -> 0/1 (odd channels), 1 -> 2/3 (even channels)

        // TODO TODO maybe redo numbering st requires minimal bitwise operations
        // to set demux_states (keep in mind FET and demux numbering needs to
        // match.
        // maybe matching is would be the most important constraint?)
        // TODO i suppose if all 4(-6) bit channel numbers are valid, i could
        // just directly translate those to demux_states, and see what that
        // numbering is?
        
        // TODO TODO in future boards, wire select pins such that I can use the
        // intuitive FET numbering and pass channel bits in directly without
        // altering

        // first just take 2 MSB of channel and sent to 2 LSB of register
        // to be consistent w/ significance <-> 595 pin number correspondence
        // in FET registers (2 MSB = and with 0b1100.)
        // checked w/ v0.1 board. does not need swapping.
        demux_states = (uint8_t) (demux_states | (channel & 0xC) >> 2);
       
        // 2 LSB -> 2 MSB
        // TODO see if needs swapped
        demux_states = (uint8_t) (demux_states | (channel & 0x3) << 2);

        // now need to mask those two bits (with 0b0011 = 3), 
        // TODO determine whether we also need to switch 4052 bits
        /*
        demux_states = (uint8_t) (demux_states | \
            (channel & 0x8) << lowest_demux_state_bit);
        */
        // TODO 0b1100=12=0xC if reversed
        /*demux_states = (uint8_t) (demux_states | \
            channel << lowest_demux_state_bit);
        */

        // TODO test these states are set correctly (at least that
        // demux_enable_bit doesn't clobber any of the other bits)

        // update values in shift registers
        // we only changed bits on last one, but they are all daisy chained.
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    // TODO might want to move this to the top if i don't end up needing other
    // functions only declared in here
    void init() {
        // TODO TODO do SRs lose state upon reboot (for sure)? explicitly clear?
        fet_states = 0;
        demux_states = 0;

        curr_channel_index = 0;
        next_free_index = 0;
        for (uint8_t i=0;i<num_channels;i++) {
            to_measure[i] = no_channel;
        }

        // maybe define some bit pattern (effective) constants here?
        // particularly if i'm having trouble w/ binary literals
        #if defined(ARDUINO)
            // TODO maybe check if we are using certain boardtypes w/ Arduino
            // defines to use port manipulation optimizations?
            pinMode(ser, OUTPUT);
            pinMode(srclk, OUTPUT);
            pinMode(srclr, OUTPUT);
            pinMode(rclk, OUTPUT);
            pinMode(fet_enbl, OUTPUT);
            pinMode(demux_enbl, OUTPUT);

            // TODO make a wrapper function that sets a pin to output and sets
            // initial state? maybe a macro? (would make sure all initial states
            // are software defined)

            // TODO TODO should the circuit be designed such that all inputs low
            // is a valid initial state? (probably w/ inverters and such)
            digitalWrite(ser, HIGH);
            digitalWrite(srclk, HIGH);
            // sending this s.r. pin LOW clears the bits
            digitalWrite(srclr, LOW);
            digitalWrite(rclk, HIGH);

            // LOW on output enable enables the shift register
            // and the isolation inverts the logic
            digitalWrite(fet_enbl, HIGH);
            digitalWrite(demux_enbl, HIGH);
        #endif
    }

    // SR pins go from F1-16 in order through first two SRs
    // in v0.1, F1=bottom right, F2=bottom left (w/ D-Sub connector of floor
    // down) ..., F16=top left

    /* TODO 
     * NOTE: Channels are numbered starting from 0 (to 15).
     */
    void start_shock(channel_t channel) {
        // get the bit that corresponds to this channel number
        // and OR in the bit for this channel number (make it a 1 if it wasn't)
        // to the bit-vector holding state of the two stimulus shift registers
        // TODO fix Werror conversion error / warning
        // "to ‘msk::fet_mask_t {aka short unsigned int}’ from ‘int’"
        // types:
        // fet_states - fet_mask_t (uint16_t)
        // 1 - (int? what is 0x1? way to get a char literal?)
        // channel - channel_t (uint8_t)
            //fet_states |= (uint16_t) (((uint16_t) 1) << ((uint16_t) channel));
        //
        // TODO no errors here, so does that mean that (uint16_t | uint16_t) 
        // is not uint16_t?
        // TODO TODO the question now is just whether the error *was* actually 
        // something to worry about, and this is just masking it.
        // is there a chance of this not being what I'd expect?
        fet_states = (fet_mask_t) (fet_states | (((fet_mask_t) 1) << channel));
        //
        // neither of these lines cause a Werror conversion err:
        // fet_states = (uint16_t) fet_states;
        // fet_states = (uint16_t) (((uint16_t) 1) << channel);
        //fet_states = (uint16_t) fet_states | (uint16_t) (((uint16_t) 1) <<
        //channel);
        // TODO so this is because | operands are promoted to "int"? 
        
        // TODO does actually passing the parameter make things more 
        // complicated to optimize? (to shift_out) might save on code size
        // if not inlined...
        
        // shift all the bits out (from fet_states to registers) again
        // including (and starting with) the 5 measurement-related bits
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    /* TODO 
     * NOTE: Channels are numbered starting from 0 (to 15).
     */
    void stop_shock(channel_t channel) {
        fet_states &= 0 << channel;
        #if defined(ARDUINO)
            update_registers();
        #endif
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
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    /* Sets bits such that (even) when the FET shift registers are enabled, NO
     * channels will receive voltage.
     */
    void stop_all_shock() {
        fet_states = no_fets;
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    /* Sets bits such that (only) when the FET shift registers are enabled, 
     * AT LEAST all of the left channels will receive voltage.
     *
     * Does not change voltage at any of the right channels.
     */
    void start_shock_left() {
        fet_states |= all_left;
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    /* Sets bits such that (even) when the FET shift registers are enabled, the 
     * left channels will not receive voltage.
     *
     * Does not change voltage at any of the right channels.
     */
    void stop_shock_left() {
        fet_states &= all_right;
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    /* Sets bits such that (only) when the FET shift registers are enabled, 
     * AT LEAST all of the right channels will receive voltage.
     *
     * Does not change voltage at any of the left channels.
     */
    void start_shock_right() {
        fet_states |= all_right;
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    /* Sets bits such that (even) when the FET shift registers are enabled, the 
     * right channels will not receive voltage.
     *
     * Does not change voltage at any of the left channels.
     */
    void stop_shock_right() {
        fet_states &= all_left;
        #if defined(ARDUINO)
            update_registers();
        #endif
    }

    /* Returns a measurement_t (>= measurement_bits bits in type) read
     * as soon as possible, without interacting with to_measure queue.
     * 
     * Assumes inputs are already enabled. (?)
     */
    measurement_t measure(channel_t channel) {
        // TODO maybe test if i get some hardware / simulator test setup going
        measurement_t measurement;
        _select_input_channel(channel);
        // TODO how to replace things like analogRead in a good way for testing?
        // would kind of like to replace it w/ boundary cases + expected cases
        // but I'd probably have to refactor?
        #ifdef ARDUINO
            measurement = analogRead(current_signal);
        #else
            //  10 bits: 0011 1111 1111
            // hex (Ox):    3    F    F
            // (decimal 1023 = 2^10-1)
            measurement = 0x3FF;
        #endif
        return measurement;
    }

    // TODO consider returning channel_measurement_t type regardless
    // or offering both. might depend on whether processing responses
    // in real time (w/ host sending channel nums)
    /* (like this)
    channel_measurement_t measure(channel_t channel) {
        channel_measurement_t ret;
        _select_input_channel(channel);
        // TODO need to set to zero? just a waste of a cycle?
        ret |= channel << 

    }
    */

    // TODO below / above / both? both, but prohibit mixing somehow?
    // maybe compile time flag to pick one?

    /* Returns 1 (which evaluates true) if channel is already queued to be 
     * measured. Returns 0 (which evaluates false), otherwise.
     */
    uint8_t will_be_measured(channel_t channel) {
        channel_t c;
        // could maybe get smaller overall code by making another function
        // that returns index, and then wrapping it here, just returning if 
        // index in range. then, could use index find in stop_measurement too.
        for (uint8_t i=0;i<num_channels;i++) {
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
        // TODO also check valid channel numbers with this / other flags?
            if (will_be_measured(channel)) {
                return;
            }
            // TODO or is it more important to check next_free_index <
            // num_channels?
        #endif
        // TODO input w/ channel of no_channel would really fuck things up
        // i could check for it, but i don't know if someone would do that...
        to_measure[next_free_index] = channel;
        // TODO way to inspect this internal state (but only in the context
        // of unit testing, otherwise disallow)?
        next_free_index++;
    }

    /* Removes channel from channels to being measured.
     * See measure() documentation.
     */
    void stop_measurement(channel_t channel) {
        uint8_t i;
        channel_t c;
        // find the current index of channel (if it exists)
        for (i=0;i<num_channels;i++) {
            // TODO unit test. bounds, not there, etc
            c = to_measure[i];
            if (c == channel) {
                // i = index of element we want to remove
                break;
            } else if (c == no_channel) {
                // so next_free_index won't decrease below zero
                // TODO unit test and try to make it, though
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
        channel_measurement_t channel_measurement;
        measurement_t measurement;

        // we don't have any channels in the to_measure queue
        // return no_channel error code, w/ zero measurement
        // TODO include in docs that measurement will be zero in this case
        if (next_free_index == 0) {
            channel_measurement = ((channel_measurement_t) no_channel) \
                << measurement_bits;
            return channel_measurement;
        }
        channel_measurement = 0;

        // I would have thought it was zero-initialized by default, but the
        // compiler was complaining as if it wasn't.
        channel_t channel = to_measure[curr_channel_index];
        // TODO TODO if no measurement is queued, need to return here w/o
        // selecting channel or reporting measurement
       
        // if the current index (and perhaps also adjacent lower indices) have
        // had their channels removed, reset the channel to the lowest (zero)
        // index.
        // this may be another avenue by which channels with lower indices get
        // priority over others...
        // TODO measure / test in some capacity
        if (channel == no_channel) {
            // return data with channel code set to no_channel
            curr_channel_index = 0;
            channel = to_measure[curr_channel_index];
            
            // could probably move the above to stop_measurment, if I wanted
            // the timing of measure() to be more consistent that start/stop
        }

        /*
        // TODO delete me
        #ifdef UNIT_TESTING
            std::cout << "channel index: " << \
                std::to_string(curr_channel_index) << std::endl;
            std::cout << "channel: " << std::to_string(channel) << std::endl;
        #endif
        */

        // TODO maybe break out these two lines w/ preprocessor so this 
        // function can be unit tested w/ a few different values of the 
        // measurement?
    
        // switch the analog demultiplexers to the channel
        // TODO and enable them? do i ever want to disable them?
        _select_input_channel(channel);

        // TODO directly call AVR functions?
        #ifdef ARDUINO
            measurement = analogRead(current_signal);
        #else
            // 1023 (max of 10 bit range)
            measurement = 0x3FF;
        #endif

        // shift channel up to it's position in the bits of the number
        // to be returned, and OR it in
        // TODO fix Werror=conversion error
        // conversion to ‘msk::channel_measurement_t {aka short unsigned int}’ 
        // from ‘int’
        // types:
        // channel_measurement - channel_measurement_t (uint16_t)
        // channel - channel_t (uint8_t)
        // measurement_bits - uint8_t
        //channel_measurement |= ((channel_measurement_t) channel) << 
        //measurement_bits;
        channel_measurement = (channel_measurement_t) (channel_measurement | \
            ((channel_measurement_t) channel) << measurement_bits);
        /*
        // TODO delete me
        #ifdef UNIT_TESTING
            std::cout << "measurement_bits: " << \
                std::to_string(measurement_bits) << std::endl;
            std::cout << "channel, measurement bitmask: " << \
                std::bitset<sizeof(channel_measurement)*8>(channel_measurement)\
                << std::endl;
        #endif
        */

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

        /*
        #ifdef UNIT_TESTING
            std::cout << "(to_measure[curr_channel_index] == no_channel): " << \
                (to_measure[curr_channel_index] == no_channel) << std::endl;
        #endif
        */

        // TODO unit test. maybe implement some way to check curr_channel_index
        // in unit tests, and then test curr_channel_index >= num_channels
        // case
        if (curr_channel_index >= num_channels || \
            to_measure[curr_channel_index] == no_channel) {

            curr_channel_index = 0;
        }

        /*
        #ifdef UNIT_TESTING
            std::cout << "curr_channel_index (at end of measure()): " << \
                std::to_string(curr_channel_index) << std::endl;
        #endif
        */
        return channel_measurement;
    }

    // TODO is it worth a "measure_all" function?
    // return type would be more complicated...
  
    // TODO implications of inline w/o static?
    // TODO unit test
    /* Given an integer type with the channel_bits most significant bits
     * holding the channel, and the measurement_bits least significant bits
     * holding an ADC reading (or a placeholder of 0x3FF), returns the channel.
     */
    inline channel_t extract_channel(channel_measurement_t cm) {
        return (channel_t) (cm >> measurement_bits);
    }

    // TODO unit test
    /* Given an integer type with the channel_bits most significant bits
     * holding the channel, and the measurement_bits least significant bits
     * holding an ADC reading (or a placeholder of 0x3FF), returns the
     * measurement.
     */
    inline measurement_t extract_measurement(channel_measurement_t cm) {
        return (measurement_t) (cm & measurement_mask);
    }

    uint16_t _get_fet_states() {
        return fet_states;
    }

    uint8_t _get_demux_states() {
        return demux_states;
    }

    // remove all but enable getters?
    uint8_t _get_demux_select_A() {
        return (demux_states >> demux_select_A_bit) & 1;
    }

    uint8_t _get_demux_select_B() {
        return (demux_states >> demux_select_B_bit) & 1;
    }

    uint8_t _get_chan_select_A() {
        return (demux_states >> chan_select_A_bit) & 1;
    }

    uint8_t _get_chan_select_B() {
        return (demux_states >> chan_select_B_bit) & 1;
    }

    uint8_t _get_demux_enable() {
        return (demux_states >> demux_enable_bit) & 1;
    }
}
