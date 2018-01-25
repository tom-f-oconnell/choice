
// TODO TODO it looks like some people are keen on importing the c/cpp file,
// so as to get access to static variables. maybe consider, but see
// alternatives. refactoring might be better anyway, but it might come at a cost
// of some overhead, that i've been trying to minimize
#include "../src/multishock.hpp"

// TODO why does
// https://github.com/david-grs/clang_travis_cmake_gtest_coveralls_example/
// blob/master/unit_tests.cpp use angle bracket notation, though he also uses
// submodule (in same project)?
#include "gtest/gtest.h"

#include <iostream>
// for easy printing of bitvectors
#include <bitset>
// TODO do the two above just omit .h? should i on limits?
#include <limits.h>

using namespace msk;

// measurements are set to this constant for unit testing purposes
// because we don't have hardware with which to read analog values
static unsigned int unsigned_ten_bit_max = 0x3FF;

// TODO what are the two preceding colons?
class MSKTest : public ::testing::Test {
    protected:
        virtual void SetUp() {
            init();
        }

    // TODO are there variables that i want to use?
    // TODO should i be wrapping all the state in msk in a class? might make
    // testing easier? but maybe only if still breaking encapsulation in a way
    // that is undesirable.
};

TEST_F(MSKTest,  NothingMeasuredInitially) {
    for (int i=0; i<num_channels; i++) {
        ASSERT_FALSE(will_be_measured((channel_t) i));
    }

    // check the special number indicating end of list of measured channels
    // also yields a false here
    ASSERT_FALSE(will_be_measured(no_channel));
}

/* check the returned channels by measure() are no_channel
 * which indicates a measurement was requested when no channels
 * were queued
 */
TEST_F(MSKTest,  NoChannelWhenNothingQueued) {
    channel_measurement_t cm; // uint16_t
    channel_t c;              // uint8_t
    measurement_t m;          // uint16_t (measurement_bits == 10)

    channel_measurement_t m_mask;
    // TODO define in common place
    m_mask = 0;
    for (int i=0; i<measurement_bits; i++) {
        m_mask = (channel_measurement_t) (m_mask |
            ((channel_measurement_t) 1) << i);
    }
    // TODO replace other references to m_mask with measurement_mask if this
    // works
    ASSERT_EQ(m_mask, measurement_mask);

    for (int i=0; i<num_channels; i++) {
        cm = measure();
        m = (measurement_t) (cm & m_mask);
        ASSERT_EQ(m, 0);
        c = (channel_t) (cm >> measurement_bits);
        ASSERT_EQ(c, no_channel);
    }
}

// TODO assert no_channel can fit in channel_bits
// and measurement_mask in measurement_bits

TEST_F(MSKTest, StartStopMeasurements) {
    for (int i=0; i<num_channels; i++) {
        start_measurement((channel_t) i);
        ASSERT_TRUE(will_be_measured((channel_t) i));
    }

    for (int i=0; i<num_channels; i++) {
        ASSERT_TRUE(will_be_measured((channel_t) i));
    }

    // removing in same order they were added. may want to test others.
    for (int i=0; i<num_channels; i++) {
        stop_measurement((channel_t) i);
    }

    for (int i=0; i<num_channels; i++) {
        ASSERT_FALSE(will_be_measured((channel_t) i));
    }
    // TODO pick random order for removal / insertion (seeded, maybe a few)?
}

// TODO way to unit test both this and compilation w/ check duplicates flag
// simultaneously? (CHECK_Q_DUPLICATES)

// TODO tests to make sure start / stop order, etc, can not lead to 
// pathological states like one channel not being measured, etc

// TODO TODO no state is carrying over test-to-test is it?
// TODO more descriptive test name
TEST_F(MSKTest, MeasureWithQueue) {
    channel_measurement_t cm; // uint16_t
    channel_t c;              // uint8_t
    measurement_t m;          // uint16_t (measurement_bits == 10)

    // TODO just make these masks in the text fixture, and test them
    // with one test beyond that?
    channel_measurement_t m_mask, c_mask;
    m_mask = 0;
    for (int i=0; i<measurement_bits; i++) {
        //m_mask |= ((channel_measurement_t) 1) << i;
        m_mask = (channel_measurement_t) (m_mask |
            ((channel_measurement_t) 1) << i);
    }

    c_mask = 0;
    for (int i=0; i<channel_bits; i++) {
        c_mask = (channel_measurement_t) (c_mask |
            ((channel_measurement_t) 1) << (i + measurement_bits));
    }

    // TODO print out masks and check they look correct / maybe actually compare
    // to strings or something

    // TODO check # of bits correct, fits in size of container type, and masks
    // match up
    // measurement_bits + channel_bits <= 8 * sizeof(channel_measurement_t)
    ASSERT_LE(measurement_bits + channel_bits, \
        8 * sizeof(channel_measurement_t)) << "Not enough bits to store " << \
        "both a channel and a measurement.\n";

    // not that meaningful, since masks are generated in here...
    // TODO if / when make helper functions for masks, test here
    ASSERT_EQ(c_mask & m_mask, 0) << \
        "Channel and measurement masks overlapped.\n";

    // TODO TODO make convenience functions for recovering channel and
    // measurement, and test those (though I might just pass to python.)
    // TODO anyway to do mixed python and cpp unit tests?
   
    // bitsets are formatted below with this assumption
    EXPECT_EQ(CHAR_BIT, 8) << "There seem to not be 8 bits in a byte." << \
        " Format of channel_measurement_t bitset will not be correct.\n";
    
    // if each channel is measured after being added, the channel reported by
    // measure should always be the number of the last added channel
    // (exception: empty->start one channel->measure will cause a state where
    //  the current measure_ment index is zero again. see "continue" case.)
    //  TODO so do i want it to behave s.t. new channels get some slight
    //  boost in priority upon being added? (i suppose this only happening once
    //  is OK)
    for (int i=0; i<=num_channels; i++) {
        // doesn't make sense to start a (num_channels+1)th measurement
        // but we do want to check the last measure() call result
        // (when the channel should be num_channels - 1)
        if (i < num_channels) {
            start_measurement((channel_t) i);
        }
        if (i == 0) {
            continue;
        }
        cm = measure();
        /*
        std::cout << "channel (" << std::to_string(channel_bits) << \
            " bits) + measurement (" << std::to_string(measurement_bits) << \
            " bits) returned from " << "measure() call: " << \
            std::bitset<sizeof(cm)*8>(cm) << std::endl;
        */

        // TODO provide a mechanism to set this to arbitrary values within
        // the tested functions, mocking analogRead
        m = (measurement_t) (cm & m_mask);
        ASSERT_EQ(m, unsigned_ten_bit_max);

        // TODO maybe take note here and don't try to mask channel explicitly?
        ASSERT_EQ((cm & c_mask) >> measurement_bits, cm >>
            measurement_bits);

        c = (channel_t) (cm >> measurement_bits);
        // TODO really need to cast? compare value or actually types as well?
        ASSERT_EQ(c, (channel_t) (i - 1));
    }
}

TEST_F(MSKTest, StartStopMeasureLast) {
    channel_measurement_t cm; // uint16_t
    channel_t c;              // uint8_t
    measurement_t m;          // uint16_t (measurement_bits == 10)

    channel_measurement_t m_mask;
    m_mask = 0;
    for (int i=0; i<measurement_bits; i++) {
        m_mask = (channel_measurement_t) (m_mask |
            ((channel_measurement_t) 1) << i);
    }

    for (int i=0; i<num_channels; i++) {
        start_measurement((channel_t) i);
    }
    // throw away 15 measurements, just to get to the last position possible
    for (int i=0; i<(num_channels-1); i++) {
        cm = measure();
        m = (measurement_t) (cm & m_mask);
        ASSERT_EQ(m, unsigned_ten_bit_max);
        c = (channel_t) (cm >> measurement_bits);
        ASSERT_EQ(c, i);
    }

    // then we will remove this last element, which should make the next
    // call to measure() return channel number 0 (and next will return 1)
    stop_measurement(num_channels - 1);
    cm = measure();
    m = (measurement_t) (cm & m_mask);
    ASSERT_EQ(m, unsigned_ten_bit_max);
    c = (channel_t) (cm >> measurement_bits);
    ASSERT_EQ(c, 0);

    // then will test we can re-populate this position
    start_measurement(num_channels - 1);

    // testing that it worked by measuring out to the end again
    // i=1, because we expect first measure call to return 1
    for (int i=1; i<num_channels; i++) {
        cm = measure();
        m = (measurement_t) (cm & m_mask);
        ASSERT_EQ(m, unsigned_ten_bit_max);
        c = (channel_t) (cm >> measurement_bits);
        ASSERT_EQ(c, i);
    }
    cm = measure();
    m = (measurement_t) (cm & m_mask);
    ASSERT_EQ(m, unsigned_ten_bit_max);
    c = (channel_t) (cm >> measurement_bits);
    ASSERT_EQ(c, 0);
}


const uint8_t invalid_bit = 2;
const uint8_t want_a = 0;
const uint8_t want_b = 1;

uint8_t channel_to_demux_select(channel_t channel, uint8_t a_or_b) {
    uint8_t q;
    // ranges taken from schematic (though schematic numbers channels from 1)
    if (channel <= 3) {
        // 4052 U3: 4556 Q0 LOW
        q = 0;
    } else if (channel >= 4 && channel <= 7) {
        // 4052 U4: 4556 Q1 LOW
        q = 1;
    } else if (channel >= 8 && channel <= 11) {
        // 4052 U5: 4556 Q2 LOW
        q = 2;
    } else if (channel >= 12 && channel <= 15) {
        // 4052 U6: 4556 Q3 LOW
        q = 3;
    } else {
        return invalid_bit;
    }

    uint8_t a, b;
    // from 4556 truth table
    if (q == 0) {
        a = 0;
        b = 0;
    } else if (q == 1) {
        a = 1;
        b = 0;
    } else if (q == 2) {
        a = 0;
        b = 1;
    } else if (q == 3) {
        a = 1;
        b = 1;
    } else {
        return invalid_bit;
    }

    if (a_or_b == want_a) {
        return a;
    } else if (a_or_b == want_b) {
        return b;
    } else {
        return invalid_bit;
    }
}

uint8_t channel_to_chan_select(channel_t channel, uint8_t a_or_b) {
    const uint8_t channels_per_chip = 4;

    // should model the connectivity in the schematic
    uint8_t output_channel = channel % channels_per_chip;

    uint8_t a, b;
    // from 4052 truth table
    if (output_channel == 0) {
        a = 0;
        b = 0;
    } else if (output_channel == 1) {
        a = 1;
        b = 0;
    } else if (output_channel == 2) {
        a = 0;
        b = 1;
    } else if (output_channel == 3) {
        a = 1;
        b = 1;
    } else {
        return invalid_bit;
    }

    if (a_or_b == want_a) {
        return a;
    } else if (a_or_b == want_b) {
        return b;
    } else {
        return invalid_bit;
    }
}

/* Test that defined demux chip / channel / enable bits (which are used in less
 * optimized debugging gets) agree with bits set groupwise in
 * _select_input_channel.
 */
// TODO also do hardware integration test, or test of shifting out somehow
// because in order for the whole thing to work. the internal state needs to be
// correct, as well as the shift order, s.t. the order on the hardware matches
// the internal order.
TEST_F(MSKTest, SelectInputChannelBits) {
    channel_t c;
    uint8_t actual_bit, ideal_bit;

    for (c=0; c<num_channels; c++) {
        // changes bits in demux_states (can not update_registers() w/o
        // hardware)
        _select_input_channel(c);

        actual_bit = _get_demux_select_A();
        ideal_bit = channel_to_demux_select(c, want_a);
        // TODO can i put this kind of assert in a non-test, especially if
        // the non-test function is only called from tests?
        ASSERT_NE(ideal_bit, invalid_bit) << "channel decoding functions " \
            << "in test suite failed\n";
        ASSERT_EQ(actual_bit, ideal_bit) << "unexpected demux_select_A bit";

        actual_bit = _get_demux_select_B();
        ideal_bit = channel_to_demux_select(c, want_b);
        ASSERT_NE(ideal_bit, invalid_bit) << "channel decoding functions " \
            << "in test suite failed\n";
        ASSERT_EQ(actual_bit, ideal_bit) << "unexpected demux_select_B bit";

        actual_bit = _get_chan_select_A();
        ideal_bit = channel_to_chan_select(c, want_a);
        ASSERT_NE(ideal_bit, invalid_bit) << "channel decoding functions " \
            << "in test suite failed\n";
        ASSERT_EQ(actual_bit, ideal_bit) << "unexpected chan_select_A bit";

        actual_bit = _get_chan_select_B();
        ideal_bit = channel_to_chan_select(c, want_b);
        ASSERT_NE(ideal_bit, invalid_bit) << "channel decoding functions " \
            << "in test suite failed\n";
        ASSERT_EQ(actual_bit, ideal_bit) << "unexpected chan_select_B bit";

        // no matter the channel, the enable bit should not change
        actual_bit = _get_demux_enable();
        // see notes in multishock.cpp about demux_enabled
        ASSERT_EQ(actual_bit, 0);

        // TODO maybe also check both commands don't always return the same
        // answer or something? / that 16 different patterns are returned?

        //std::cout << "checking channel: " << std::to_string(c) << std::endl;
        //std::cout << std::bitset<8>(_get_demux_states()) << std::endl;
    }
}

// TODO MeasureIndexPastRange
// TODO what happens if stuff is removed st measures index no longer points
// to a channel number?

// TODO error code if try to measure with nothing
