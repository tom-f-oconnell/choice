// Author: Tom O'Connell <toconnel@caltech.edu>

#include <stimuli.hpp>
#include <multishock.hpp>
#include <ros.h>

// will use fet_enbl pin (output enable on shift register controlling FETs)
// to switch shock on and off, just as I used to use pins for this


static choice::channel_measurement_micros cm_stamped;
// static cause problems?
static ros::Publisher("channel_measurements", &cm_stamped);

// TODO make ROS msg type for this in choice package, and include generation as
// w/ stimuli package?
void send_measurement() {
  // should be 16 bits.
  msk::channel_measurement_t cm;
  cm = msk::measure();
  // should wrap around every 70 minutes or so. will need to take in to account.
  // TODO maybe it is unrealistic to ever be able to get two "packets" sent in a
  // millisecond though? 

}

void setup() {
  // TODO make sure these don't conflict
  msk::init();
  stim::init();

  // TODO get nh from stim?
  nh.advertise

  msk::start_measuring_all();
  msk::start_shock_all();

  stim::while_idle(send_measurement);
}

void loop() {
  // would be simpler... but i feel like i need more control to get the
  // measurements back out too, unless i make could also register functions w/
  // (arbitrary?) return types easily
  stim::update();
}

