// Author: Tom O'Connell <toconnel@caltech.edu>

#include <stimuli.hpp>
#include <multishock.hpp>
// TODO how to publish w/o nodehandle? should be able to...
#include <ros.h>
// TODO include this generated type in multishock library?
#include <choice/ChannelMeasurementMicros.h>

// will use fet_enbl pin (output enable on shift register controlling FETs)
// to switch shock on and off, just as I used to use pins for this


static choice::ChannelMeasurementMicros cm_stamped;
// static cause problems?
// TODO why does it need to be initialized w/ address, and then also passed
// address on call to publish?
static ros::Publisher measurement_pub("channel_measurements", &cm_stamped);

// TODO make ROS msg type for this in choice package, and include generation as
// w/ stimuli package?
void send_measurement() {
  // should be 16 bits.
  msk::channel_measurement_t cm;
  // TODO might be faster / preferable to just measure each channel explicitly
  // in a for loop
  cm_stamped.channel_measurement = msk::measure();
  // should wrap around every 70 minutes or so. will need to take in to account.
  // TODO maybe it is unrealistic to ever be able to get two "packets" sent in a
  // millisecond though? 
  cm_stamped.micros = micros();
  
  measurement_pub.publish(&cm_stamped);
}

void setup() {
  // TODO make sure these don't conflict
  msk::init();
  // TODO provide function to publish / get nodehandle if necessary
  // maybe get rid of ROS import?
  stim::init();

  // TODO get nh from stim?
  stim::get_nodehandle->advertise(measurement_pub);
  stim::while_idle(send_measurement);

  msk::start_measuring_all();

  // should disable FET register output
  // will control shock to flies with this pin
  digitalWrite(msk::fet_enbl, LOW);
  // will control shock w/ enable pin
  msk::start_shock_all();
}

void loop() {
  // would be simpler... but i feel like i need more control to get the
  // measurements back out too, unless i make could also register functions w/
  // (arbitrary?) return types easily
  stim::update();
}

