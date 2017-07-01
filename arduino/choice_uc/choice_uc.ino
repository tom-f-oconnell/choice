#include <Servo.h>

// only one vacuum solenoid, and a few rotary switches redirecting the flow
#define VACUUM_VALVE_PIN    4
#define SORTER_PULSE_PIN    5
#define SORTER_DIR_PIN      6
#define SORTER_ENBL_PIN     7
#define STEPDRIVER_PULSE_MS 5
#define STEPS_PER_REV       200
#define SORTER_POSITIONS    10

// TODO if vacuum is too weak to suck flies out, divided across 8 chambers
// may need to have a 3rd sorter, not linked to the first two
// (and probably a mutually sealed position for the existing two sorters)

// input sorter: unused position
// output sorter: all conditioning chambers -> water vacuum trap -/-> house vac
// postions in range [0,9]
#define CLEARING_SORTER_POSITION 0
#define SEALED_SORTER_POSITION   1
//remaining positions will deal with vacuum traps

#define SERVO_WAIT_TIME_MS   500
#define TRAP_VALVE_TIME_MS   6000
#define EGRESS_VALVE_TIME_MS 5000
// TODO remove? still used?
#define NUM_PINS             20
#define NUM_TRAPS            1

#define ENTRY_CONTROL_PIN    2
#define EGRESS_SLIDER_PIN    3
#define FIRST_TRAP_PIN       8
// TODO rename
#define INTERRUPT_PIN        A0

// (degrees)
#define BLOCKED    130
#define OPEN       140

#define EXPERIMENT 132
#define EGRESS     147

// head attached in TRAP_READY position after servo is written to 180 degrees.
#define TRAP_READY 160
#define TRAP_OPEN  93

#define TRAP_EXIT_THRESHOLD 800

typedef boolean (*function)();

// 1 servo to control slider to vacuum flies out
// 1 servo to control flies entering system from vial
const int NUM_SERVOS = NUM_TRAPS + 2;

Servo servos[NUM_PINS];

const int TEST_DELAY = 2000;

// be careful if this doesn't divide evenly (best to make it do so)
const int steps_per_pos = STEPS_PER_REV / SORTER_POSITIONS;
unsigned int current_steps = 0;

// TODO remove
// pins these servos are on
//const unsigned char egress_slider = 2;
//const unsigned char trap1 = 8;

// TODO consider renaming full / fly_left for readability
boolean full[NUM_TRAPS];
boolean fly_left[NUM_TRAPS];
int trap_servo_pins[NUM_TRAPS];
int trap_exit_sensors[NUM_TRAPS];

// TODO make timer based w/ global update if necessary
void move_servo(int pin, int deg) {
  Servo s = servos[pin];
  s.attach(pin);
  s.write(deg);
  delay(SERVO_WAIT_TIME_MS);
  s.detach();
}

void stepper_driver_pulse(int pin) {
  digitalWrite(pin, HIGH);
  // TODO consider increasing
  delay(STEPDRIVER_PULSE_MS);
  digitalWrite(pin, LOW);
}

// TODO might be hard to make non-blocking
// might also consider only switching ENBL on at beginning
// DIR is only set once (not switching directions should make backlash less of a 
// problem)
void position_sorters(unsigned int goal_pos) {
  unsigned int goal_steps = goal_pos * steps_per_pos;
  // would otherwise loop forever if goal_steps >= STEPS_PER_REV
  if (goal_steps >= STEPS_PER_REV) {
    return;
  }
  
  digitalWrite(SORTER_ENBL_PIN, HIGH);
  while (current_steps != steps_per_pos) {
    stepper_driver_pulse(SORTER_PULSE_PIN);
    // TODO check correct
    current_steps = (current_steps + 1) % STEPS_PER_REV;
  }
  // TODO additional delay for it to finish step? do pulses buffer or 
  // are they completed immediately (probably later)
  digitalWrite(SORTER_ENBL_PIN, LOW);
}

void vacuum_pulse(unsigned int duration_ms) {
  digitalWrite(VACUUM_VALVE_PIN, HIGH);
  delay(duration_ms);
  digitalWrite(VACUUM_VALVE_PIN, LOW);
}

/* other positions should work OK if horns set relative to this.
   (used for calibration) */
void move_all_trap_servos_to_145() {
  for (int i=0;i<NUM_TRAPS;i++) {
    move_servo(trap_servo_pins[i], 145);
  }
}

void move_all_servos_to_145() {
  // TODO
}

void ready_experiment() {
  move_servo(EGRESS_SLIDER_PIN, EXPERIMENT);
  // TODO move egress sorter (if using) to closed position
  // move input sorters to a valid position
}

// TODO maybe change design such that i can suck individual flies out later?
// way to do it w/o changing design?
void end_experiment() {
  move_servo(EGRESS_SLIDER_PIN, EGRESS);
  // TODO use rotary valve or something to limit available vacuum pressure
  // to one channel at a time, if necessary to remove flies reliably
  position_sorters(CLEARING_SORTER_POSITION);
  vacuum_pulse(EGRESS_VALVE_TIME_MS);
  // better state to finish in?
  position_sorters(SEALED_SORTER_POSITION);
}

boolean fly_exiting_vial() {
  // TODO TODO TODO
  // may have to debounce / filter somehow
  //return digitalRead(INTERRUPT_PIN);
  return true;
}

// since Arduino Uno / Nano only has 5 Analog inputs, and I may need 8
// i'm just getting an Arduino Mega, which has 16 analog inputs
// alternatives: daisy chain arduinos, multiplex sensors, pick resistors such that
// digital pins can detect fly entering trap

// TODO could also possibly get this information from ROS tracking
// have to actuate the trap later than otherwise would (and fly might 
// fall a few times and be delayed in the meantime) with this approach.
// wouldn't check traps individually. would just check for signal that any
// were vacated.

/*
// fly passing sensor *should* correspond to a drop in reflectivity
boolean fly_exiting_trap(int i) {
  // TODO do i need to use different thresholds across traps?
  // TODO debounce / filter?
  return analogRead(trap_exit_sensors[i]) < TRAP_EXIT_THRESHOLD;
}
*/

void wait_for(function f) {
  while (!(*f)()) { ; }
}

// TODO how to accept variable length bool array? sizeof(boolean) = 1 byte?
// in an array do they still each take up 1 byte? bit?
boolean all_full() {
  for (int i=0;i<NUM_TRAPS;i++) {
    if (!full[i]) {
      return false;
    }
  }
  return true;
}

// returns the index of a randomly selected empty chamber
int get_empty() {
  // loops forever if all full
  while (true) {
    // [0,NUM_TRAPS) (traps indexed from zero, so should be correct)
    int n = random(NUM_TRAPS);
    if (!full[n]) {
      return n;
    }
  }
}

/*
// TODO could coordinate w/ ROS if i don't want to use separate sensors
void close_vacated_traps() {
  for (int i=0;i<NUM_TRAPS;i++) {
    if (full[i] && !fly_left[i]) {
      if (fly_exiting_trap(i)) {
        // TODO maybe wait / filter (also) here?
        move_servo(trap_servo_pins[i], TRAP_READY);
        fly_left[i] = true;
      }
    }
  }
}
*/

void close_vacated_trap(char c) {
  // could probably do without the checks, but this will at least prevent trying to actuate
  // if we are alread there
  if (full[i] && !fly_left[i]) {
    // TODO check no weirdness. will need to encode in ROS
    int trap_num = c;
    move_servo(trap_servo_pins[trap_num], TRAP_READY);
    // TODO do i actually need this?
    fly_left[i] = true;
  }
}

void let_fly_in(int i) {
  move_servo(ENTRY_CONTROL_PIN, OPEN);
  move_servo(trap_servo_pins[i], TRAP_READY);
  // TODO test. boolean func working? getting called? need to dereference (&)?
  wait_for(fly_exiting_vial);
  // move sorters to current trap

  // TODO could use reflectivity sensor to test whether fly has entered
  // has advantages and disadvantages
  // apply vacuum
  vacuum_pulse(TRAP_VALVE_TIME_MS);
  // TODO maybe put this above vacuum pulse?
  move_servo(ENTRY_CONTROL_PIN, BLOCKED);
  
  // could also do this for all traps at the same time, and first
  // put the trap in an intermediate, sealed, position
  move_servo(trap_servo_pins[i], TRAP_OPEN);

  // does not indicate fly has left trap to enter choice arena
  full[i] = true;
  // maybe remove this
  fly_left[i] = false;
}

// only runs at the end of each loop(), so check it can tolerate delays
// there are more real-time ways of doing this
void serialEvent() {
  // TODO robust enough? i don't want a longer message to get fragmented though...
  char c = (char) Serial.read();
  // this character will be the signal to end the experiment
  if (c == 'E') {
    end_experiment();
  } else {
    close_vacated_trap(c);
  }
  // TODO check for errors?
}

// TODO make sure all pins / used variables #defined / declared are referenced here
void setup() {
  // make sure all pins that are supposed to be outputs are set here
  pinMode(VACUUM_VALVE_PIN, OUTPUT);
  pinMode(SORTER_PULSE_PIN, OUTPUT);
  pinMode(SORTER_DIR_PIN, OUTPUT);
  pinMode(SORTER_ENBL_PIN, OUTPUT);
  pinMode(ENTRY_CONTROL_PIN, OUTPUT);
  pinMode(EGRESS_SLIDER_PIN, OUTPUT);

  // you don't strictly need all of these calls
  // but it helps ensure near total independence from previous state of the Arduino
  digitalWrite(VACUUM_VALVE_PIN, LOW);
  digitalWrite(SORTER_PULSE_PIN, LOW);
  // TODO maybe just hard wire this to ground?
  digitalWrite(SORTER_DIR_PIN, LOW);
  digitalWrite(SORTER_ENBL_PIN, LOW);
  digitalWrite(ENTRY_CONTROL_PIN, LOW);
  digitalWrite(EGRESS_SLIDER_PIN, LOW);

  for (int i=0;i<NUM_TRAPS;i++) {
    int servo_pin = FIRST_TRAP_PIN + i;
    pinMode(servo_pin, OUTPUT);
    digitalWrite(servo_pin, LOW);
    trap_servo_pins[i] = servo_pin;

    full[i] = false;
    fly_left[i] = false;
  }

  // INPUT is the default pin mode, but just to be clear
  pinMode(INTERRUPT_PIN, INPUT);

  // TODO make some calibration functions
  //move_all_trap_servos_to_145();
  ready_experiment();
}

/* TODO:
-how to coordinate experiment state w/ ROS nodes (when to suck flies in/out,
 ,etc)?
-is this also controlling shock? may need more pins then? (maybe just 1, or shift)
-drive sorter gears only in one direction
-pick chamber to send fly to randomly from available (not sequential) 
-NEED TO REWRITE let_fly_in TO ACCOMODATE CONSTANT CHECKS FOR FLIES WALKING INTO
 CHAMBERS FROM TRAPS (by checking reflectivity sensors)
*/

void loop() {
  // TODO will also probably need to check for vacated traps (separately?)
  while (!all_full()) {
    int chamber_num = get_empty();
    let_fly_in(chamber_num);
  }
  // TODO the arduino could technically be put into a lower power state when
  // all_full. may not be of any value.

  // TODO support sNN{L/R}, cNN, end (anything else?)
  // a reason to send which chambers are full to ROS: could not track some chambers unless a fly is expected
  

  // this is where serialEvent checks to for input
  // (ROS nodes may send the Arduino a character telling it to end the experiment)
  // TODO refactor everything to check this more frequently (less blocking) (the check for vacated traps at least)
}
