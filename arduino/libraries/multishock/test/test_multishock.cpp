
// TODO which order should this import go in again? matters, right?
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

// TODO what are the two preceding colons?
class MSKTest : public ::testing::Test {
    protected:
        virtual void SetUp() {
            init();
        }

    // TODO are there variables that i want to use?
    // TODO should i be wrapping all the state in msk in a class?
};

TEST_F(MSKTest,  NothingMeasuredInitially) {
    for (int i=0; i<num_channels; i++) {
        ASSERT_FALSE(will_be_measured((channel_t) i));
    }
}

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

    // TODO make convenience functions for recovering channel and measurement,
    // and test those (though I might just pass to python.)
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

        // for now, the 0x3FF (1023) is a constant for each measurement
        // called within a unit test
        // TODO provide a mechanism to set this to arbitrary values within
        // the tested functions, mocking analogRead
        m = (measurement_t) (cm & m_mask);
        ASSERT_EQ(m, 0x3FF);

        // TODO maybe take note here and don't try to mask channel explicitly?
        ASSERT_EQ((cm & c_mask) >> measurement_bits, cm >>
            measurement_bits);

        c = (channel_t) (cm >> measurement_bits);
        // TODO really need to cast? compare value or actually types as well?
        ASSERT_EQ(c, (channel_t) (i - 1));
    }
}

// TODO use a variable for all of these 0x3FF measurement placeholders

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
        ASSERT_EQ(m, 0x3FF);
        c = (channel_t) (cm >> measurement_bits);
        ASSERT_EQ(c, i);
    }

    // then we will remove this last element, which should make the next
    // call to measure() return channel number 0 (and next will return 1)
    stop_measurement(num_channels - 1);
    cm = measure();
    m = (measurement_t) (cm & m_mask);
    ASSERT_EQ(m, 0x3FF);
    c = (channel_t) (cm >> measurement_bits);
    ASSERT_EQ(c, 0);

    // then will test we can re-populate this position
    start_measurement(num_channels - 1);

    // testing that it worked by measuring out to the end again
    // i=1, because we expect first measure call to return 1
    for (int i=1; i<num_channels; i++) {
        cm = measure();
        m = (measurement_t) (cm & m_mask);
        ASSERT_EQ(m, 0x3FF);
        c = (channel_t) (cm >> measurement_bits);
        ASSERT_EQ(c, i);
    }
    cm = measure();
    m = (measurement_t) (cm & m_mask);
    ASSERT_EQ(m, 0x3FF);
    c = (channel_t) (cm >> measurement_bits);
    ASSERT_EQ(c, 0);
}

/*
TEST_F(MSKTest, MeasureIndexPastRange) {
    // TODO what happens if stuff is removed st measures index no longer points
    // to a channel number?
}

// TODO error code if try to measure with nothing

*/

/*
TEST_F(MSKTest,) {
}
*/
