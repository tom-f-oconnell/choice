// Author: Tom O'Connell <toconnel@caltech.edu>

#include <stimuli.hpp>

void setup() {
  stim::init();

  // TODO write a test to make sure no function is called when init'd w/o
  // calling stim::while_idle? too close to being tautological?

  // TODO let the host know which version of the code we have?
  // or at least err if it is asking for functionality we can not provide? e.g.
  // measurement, controlling shock with one pin, or independently controlling
  // left and right shock with only two pins
  // other differences? publish code hash as a parameter anyway? (would probably
  // need to do this outside of Arduino? maybe with the preprocessor...)

  // The other issue is now that the Arduino could have a control circuitry
  // shield connected that is incompatible with the current version of the code,
  // or with the configuration that is used to run the experiment.
  // Could solve with some kind of hardware ID on the shield? One of two
  // pull-ups? Kind of wasteful of pins, but correctness is key...
  // Some one-wire chip? Some hacky solution where we can infer what is
  // connected to drive pins?
  // Warn if not detecting one of the version of hardware.
}

void loop() {
  // would be simpler... but i feel like i need more control to get the
  // measurements back out too, unless i make could also register functions w/
  // (arbitrary?) return types easily
  stim::update();
}

