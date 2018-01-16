/*
 * multishock.hpp - Wiring/Arduino library to control shock delivery and 
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

// TODO look at some open source devices that use shift registers similarly
// their layout, their code

#ifndef SHOCK_HPP
#define SHOCK_HPP

// this whole if statement just gets fixed bit-length type definitions
#if defined(ARDUINO)
#if ARDUINO >= 100
    #include <Arduino.h>  // Arduino 1.0
#else
    #include <WProgram.h> // Arduino 0022
#endif

#elif defined(UNIT_TESTING)
#include <stdint.h>
#endif

// TODO no Arduino issues using .hpp are there?
// I want to because using namespace in here

// [M]ulti[S]hoc[K]
namespace msk {
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
    * inputs select which channel of the active 4052 is used, and the final
    * enable pin can be used to disable all of the 4052s.
    *
    * The remaining 3 pins on the third shift register are not used.
    *
    * TODO include truth tables of 4556 and 4052? operation of 74HC595?
    * or maybe just a reference to page of datasheet for the last one?
    *
    */
    // TODO does the user of the library actually need / want these?
    // maybe move to .cpp?
    // TODO more clear to suffix w/ "pin"?
    const uint8_t ser        = 4;
    const uint8_t srclk      = 5;
    const uint8_t srclr      = 6;
    const uint8_t rclk       = 7;
    const uint8_t fet_enbl   = 8;
    const uint8_t demux_enbl = 9;

    // TODO better way?
    // not compiled w/o ARDUINO, because otherwise A0 is not defined
    #ifdef ARDUINO
        // the input from the isolation amplifier
        // should be proportional to the current the fly received (on whichever
        // demultiplexer channels is currently selected), within the working
        // range
        const uint8_t current_signal = A0;
    #endif

    //const uint8_t shift_register_bits = 21;
    const uint16_t shiftreg_period_ms = 50;

    // TODO how were these used differently?
    //const uint16_t min_demux_period_ms = 1;
    const uint16_t period_per_channel_ms = 5000;
    //const uint16_t fet_switch_to_sample_ms = 1;

    // TODO to what extent / should i use namespaces? for things like constants?
    // functions? (vs. prefix?)

    // TODO organize typdefs all at top, or just above their use?
    typedef uint8_t channel_t;
    typedef uint16_t measurement_t;
    typedef uint16_t channel_measurement_t;

    const uint8_t num_channels = 16;

    // TODO -1 work?
    // is using -1 to get the max value of an unsigned field portable? other?
    // (w/o include, ideally)
    // 63 is the highest unsigned value storable in 6 bits
    // (10 measurement bits => 6 left for channel)
    const channel_t no_channel = 63;

    // Since I think wanting more than 2^4 channels (on one Arduino) is more 
    // likely than wanting better than 10 bits of resolution on the current 
    // through each channel, I'm allotting 6 bits (64 total channels -> 
    // 32 chambers with left and right) to channel ID.

    // If you require more than 10 bits of resolution on the current, the
    // integer type will (and / or the masks) will need to change.

    // Though there are the Due, Zero, and MKR, with built in 12 bit ADCs...

    // TODO compile flag to use either 6 or 4 bits for channels?
    
    // TODO maybe use hex (stick to C, rather than GCC features) or B?
    // check __GNUC__?
    // only exactly the 10 bits the cheaper Arduinos have
    
    // TODO maybe make it easier for people to modify this?
    // allow re-defining somehow?
    const uint8_t measurement_bits = 10;
    const uint8_t channel_bits = 6;
    const channel_measurement_t measurement_mask = 0x3FF;

    void init();

    // TODO language choice other than start/stop, that is more clear it is 
    // primarily intended to change register contents. i suppose for targetting
    // single channels, it will be necessary to use start/stop_shock(channel)
    // , rather than [en/dis]abling.
    // 
    // (prepare_ / ready_) ((stop / cancel / none / ?) / all / left / right)
    // include word shock?

    // although, maybe the shock duration will be really short relative to 
    // period between wanting to add / remove chambers from being shocked?
    // in that case, it might still make sense to do a lot of [en/dis]abling

    // caller will be responsible for ensuring the channel is valid
    // (could return int if invalid... probably don't want to though)
    void start_shock(channel_t channel);
    void stop_shock(channel_t channel);

    // TODO maybe make left/right special channel nums and pass those into 
    // start/stop_shock? could use (otherwise unused) high 2 bits
    
    // TODO i'm really conflicted about whether to support stopping groups
    // of pins... resolve.

    void start_shock_left();
    void stop_shock_left();

    void start_shock_right();
    void stop_shock_right();

    // TODO maybe even in this case it'd be preferable to return 
    // channel_measurement_t? won't i essentially have to pack it that way for
    // transport to the computer anyway? (i suppose if everything is
    // transactional, maybe not...)
    // If I want this library to work in pure C contexts, I will change this
    // name to measure_now (but we are using namespaces, etc, now anyway).
    measurement_t measure(channel_t channel);

    // TODO below / above / both? both, but prohibit mixing somehow?

    uint8_t will_be_measured(channel_t channel);
    void start_measurement(channel_t channel);
    void stop_measurement(channel_t channel);

    // measure_next?
    channel_measurement_t measure();

    channel_t extract_channel(channel_measurement_t cm);
    measurement_t extract_measurement(channel_measurement_t cm);

    // TODO worth packing together 10 bit analogRead return and only sending
    // multiple at once? see Ben Krasnow "ping-pong" buffer code? (*host* word
    // length?)
    // or maybe configure ADC for reading lesser # of bits for faster
    // acquisition, and then it might make more sense?
    // (I think I'll leave sending data to the computer to the user?)
    // TODO maybe make a utility function to pack into another type, for more
    // efficient transport? + put in an example, include example Python code
  

    // TODO the face that both of these preprocessor branches were run seems
    // to suggest that Arduino is doing something weird, or I'm accidentally
    // somehow double including...

    // there might be a better way to do this. this define is intended to be set
    // just before #including this header file such that some select static
    // functions can be made non-static, for testing.

    // ONLY TO BE USED FOR TESTING PURPOSES.
    // DO NOT CALL IN EXPERIMENT / ACQUISITION CODE!!
    // TODO wrap the tests that use these in things compiled within the library?
    // and then just expose the full tests? alternative? (want Arduino to
    // compile library with different options..., but seems I can't do this
    // through IDE)
    void _clear_reg();
    void _update_output();
    void _shift(uint8_t bit);
    void _select_input_channel(channel_t channel);

    uint16_t _get_fet_states();
    uint8_t _get_demux_states();
}
#endif
