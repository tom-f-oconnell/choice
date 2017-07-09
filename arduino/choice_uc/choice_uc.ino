
#include <math.h>
#include <Servo.h>

// only one vacuum solenoid, and a few rotary switches redirecting the flow
#define VACUUM_VALVE      45
#define SORTER_STEP       53
#define SORTER_SLEEP      51
#define EXIT_SORTER_STEP  49
#define EXIT_SORTER_SLEEP 47
#define STEPDRIVER_PULSE_MS   5
#define FULL_STEPS_PER_REV    200
#define MICROSTEPPING         8
#define SORTER_POSITIONS      10
#define SORTER_ALIGNMENT_OFFSET 85

// TODO if vacuum is too weak to suck flies out, divided across 8 chambers
// may need to have a 3rd sorter, not linked to the first two
// (and probably a mutually sealed position for the existing two sorters)

// input sorter: unused position
// output sorter: all conditioning chambers -> water vacuum trap -/-> house vac
// postions in range [0,9]
#define SEALED_SORTER_POSITION   9
//remaining positions will deal with vacuum traps

#define SERVO_WAIT_TIME_MS   500
#define TRAP_VALVE_TIME_MS   6000
#define EGRESS_VALVE_TIME_MS 5000
// TODO remove? still used?
#define NUMS             54
#define NUM_TRAPS            8

// dolly can be 43 if using
#define ENTRY_CONTROL    39
#define EGRESS_SLIDER    41
#define FIRST_TRAP       23

#define FLY_ENTRY_SENSOR       A0
#define SORTER_PRESSURE_SENSOR A1

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

// TODO how to handle remaining servos? just allocate traps here?
Servo trap_servos[NUM_TRAPS];
int trap_servo_pins[NUM_TRAPS];

// be careful if this doesn't divide evenly (best to make it do so)
const int num_steps = MICROSTEPPING * FULL_STEPS_PER_REV;
const int steps_per_pos = MICROSTEPPING * FULL_STEPS_PER_REV / SORTER_POSITIONS;
unsigned int current_steps = 0;

// TODO remove
// pins these servos are on
//const unsigned char egress_slider = 2;
//const unsigned char trap1 = 8;

// TODO consider renaming full / fly_left for readability
boolean full[NUM_TRAPS];
boolean fly_left[NUM_TRAPS];
int trap_exit_sensors[NUM_TRAPS];

boolean sorter_sleeping;

// TODO make timer based w/ global update if necessary
void move_servo(int idx, int deg) {
  Servo s = trap_servos[idx];
  int pin = trap_servo_pins[idx];
  s.attach(pin);
  Serial.print("pin in move_servo ");
  Serial.println(pin);
  s.write(deg);
  delay(SERVO_WAIT_TIME_MS);
  s.detach();
}

// TODO
void ready_trap(int trap_num) {
  
}

void release_fly(int trap_num) {
  
}

// TODO what was cause of lurching on restarting stepper? these didn't 
// seem to fix the problem...
void unsleep() {
  if (sorter_sleeping) {
    digitalWrite(SORTER_SLEEP, HIGH);
    sorter_sleeping = false;
  }
}

void resleep() {
  if (!sorter_sleeping) {
    digitalWrite(SORTER_SLEEP, LOW);
    sorter_sleeping = true;
  }
}

// could play with trailing delay
void stepper_driver_pulse(int pin) {
  digitalWrite(pin, HIGH);
  delayMicroseconds(2);
  digitalWrite(pin, LOW);
  delay(21);
}

// TODO might be hard to make non-blocking
// might also consider only switching ENBL on at beginning
// DIR is only set once (not switching directions should make backlash less of a 
// problem)
void position_sorter(unsigned int goal_pos) {
  unsigned int goal_steps = goal_pos * steps_per_pos;
  finely_position_sorter(goal_steps);
}

unsigned int positive_step_angle(int step_angle) {
  // TODO is this stupid? should i just fail if <= -num_steps?
  while (step_angle < 0) {
    step_angle = step_angle + num_steps;
  }
  return (unsigned int) step_angle;
}

void finely_position_sorter(int goal_steps) {
  // would otherwise loop forever if goal_steps >= num_steps
  if (goal_steps >= num_steps) {
    return;
  }
  // TODO check
  int positive_goal_steps = positive_step_angle(goal_steps);
  Serial.println("goal position modulo steps per rev: " + \
    String(positive_goal_steps));
  unsleep();
  // TODO minimize delays. may need to find cause of jumping.
  delay(1000);
  Serial.println("current positions:");
  Serial.println(current_steps);
  while (current_steps != positive_goal_steps) {
    stepper_driver_pulse(SORTER_STEP);
    // TODO longer delay
    
    // TODO check correct
    current_steps = (current_steps + 1) % num_steps;
    Serial.println(current_steps);
  }
  // TODO additional delay for it to finish step? do pulses buffer or 
  // are they completed immediately (probably later)
  delay(1000);
  resleep();
}

void vacuum_pulse(unsigned int duration_ms) {
  digitalWrite(VACUUM_VALVE, HIGH);
  delay(duration_ms);
  digitalWrite(VACUUM_VALVE, LOW);
}

/* other positions should work OK if horns set relative to this.
   (used for calibration) */
void move_all_trap_servos_to(int deg) {
  for (int i=0;i<NUM_TRAPS;i++) {
    Serial.println(trap_servo_pins[i]);
    move_servo(i, deg);
  }
}

void ready_experiment() {
  move_servo(EGRESS_SLIDER, EXPERIMENT);
  // TODO move egress sorter (if using) to closed position
  // move input sorters to a valid position
}

// TODO maybe change design such that i can suck individual flies out later?
// way to do it w/o changing design?
void end_experiment() {
  move_servo(EGRESS_SLIDER, EGRESS);
  // TODO use rotary valve or something to limit available vacuum pressure
  // to one channel at a time, if necessary to remove flies reliably
  vacuum_pulse(EGRESS_VALVE_TIME_MS);
  // better state to finish in?
  position_sorter(SEALED_SORTER_POSITION);
}

boolean fly_exiting_vial() {
  // TODO TODO TODO
  // may have to debounce / filter somehow
  //return digitalRead(FLY_ENTRY_SENSOR);
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
        move_servo(i, TRAP_READY);
        fly_left[i] = true;
      }
    }
  }
}
*/

// TODO
/*
void close_vacated_trap(char c) {
  // could probably do without the checks, but this will at least prevent trying to actuate
  // if we are alread there
  // TODO check no weirdness. will need to encode in ROS
  int trap_idx = (int) c;
  if (full[trap_idx] && !fly_left[trap_idx]) {
    move_servo(trap_idx, TRAP_READY);
    // TODO do i actually need this?
    fly_left[trap_idx] = true;
  }
}
*/

void let_fly_in(int i) {
  move_servo(ENTRY_CONTROL, OPEN);
  move_servo(i, TRAP_READY);
  // TODO test. boolean func working? getting called? need to dereference (&)?
  wait_for(fly_exiting_vial);
  // move sorters to current trap

  // TODO could use reflectivity sensor to test whether fly has entered
  // has advantages and disadvantages
  // apply vacuum
  vacuum_pulse(TRAP_VALVE_TIME_MS);
  // TODO maybe put this above vacuum pulse?
  move_servo(ENTRY_CONTROL, BLOCKED);
  
  // could also do this for all traps at the same time, and first
  // put the trap in an intermediate, sealed, position
  move_servo(i, TRAP_OPEN);

  // does not indicate fly has left trap to enter choice arena
  full[i] = true;
  // maybe remove this
  fly_left[i] = false;
}

// TODO deal w/ exit sorter too
// want to find center position of minimum pressures (sorter aligned w/ sensor)
// and set zero relative to that position w/ a defined offset
void align_sorter() {
  current_steps = 0;
  
  Serial.println("starting sorter alignment (uses pressure sensor)...");
  int measurements[num_steps];

  double sum1 = 0;
  double sum2 = 0;

  Serial.println("measuring pressures around one full rotation...");
  unsleep();
  // TODO minimize delays
  delay(1000);
  for (int i=0;i<num_steps;i++) {
    stepper_driver_pulse(SORTER_STEP);
    measurements[i] = analogRead(SORTER_PRESSURE_SENSOR);
    Serial.print(i);
    Serial.print(": ");
    Serial.println(measurements[i]);
    sum1 += measurements[i];
  }
  delay(1000);
  resleep();

  Serial.println("calculating sensor threshold and mean motor angle...");
  // using the (at least for small n?) numerically stable 2 pass
  // variance algorithm from Wikipedia
  double mean = sum1 / num_steps;
  double diff;
  for (int i=0;i<num_steps;i++) {
    diff = ((double) measurements[i]) - mean;
    sum2 += diff*diff;
  }
  double stddev = sqrt(sum2 / num_steps);
  const double c = 1.5;
  int threshold = round(mean - c * stddev);
  Serial.println("stddev: " + String(stddev));
  Serial.println("threshold: " + String(threshold));


  // using formula from Wikipedia article on mean of circular quantities
  double sinsum = 0;
  double cossum = 0;
  double angle;
  const int two_pi = 6.2832;
  Serial.println("indices below threshold:");
  for (int i=0;i<num_steps;i++) {
    if (measurements[i] < threshold) {
      angle = two_pi * (((double) i) / num_steps);
      sinsum += sin(angle);
      cossum += cos(angle);
      Serial.println(i);
    }
  }
  int mean_lowpressure_step = round(atan2(sinsum, cossum) / two_pi  * num_steps);
  Serial.println("new zero in current coordinates: " + \
    String(mean_lowpressure_step + SORTER_ALIGNMENT_OFFSET));
  // TODO test that on a few revolutions, the minimum is in the same place?
  // sum of differences of measurement array < some threshold?

  Serial.println("moving to new zero position...");
  // current zero is where we happened to start taking measurements
  // we want to move to the center of low pressure area + offset
  // and then define that as the new zero globally
  // TODO test sorter positioning functions with negative arguments
  finely_position_sorter(mean_lowpressure_step + SORTER_ALIGNMENT_OFFSET);
  current_steps = 0;
}

void test_servos() {
  
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
    // TODO
    //close_vacated_trap(c);
  }
  // TODO check for errors?
}

// TODO make sure all pins / used variables #defined / declared are referenced here
void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  // make sure all pins that are supposed to be outputs are set here
  pinMode(VACUUM_VALVE, OUTPUT);
  pinMode(SORTER_STEP, OUTPUT);
  pinMode(SORTER_SLEEP, OUTPUT);
  pinMode(ENTRY_CONTROL, OUTPUT);
  pinMode(EGRESS_SLIDER, OUTPUT);

  // you don't strictly need all of these calls
  // but it helps ensure near total independence from previous state of the Arduino
  digitalWrite(VACUUM_VALVE, LOW);
  digitalWrite(SORTER_STEP, LOW);
  digitalWrite(SORTER_SLEEP, LOW);
  digitalWrite(EXIT_SORTER_STEP, LOW);
  digitalWrite(EXIT_SORTER_SLEEP, LOW);
  digitalWrite(ENTRY_CONTROL, LOW);
  digitalWrite(EGRESS_SLIDER, LOW);

  for (int i=0;i<NUM_TRAPS;i++) {
    int servo = FIRST_TRAP + i * 2;
    
    pinMode(servo, OUTPUT);
    digitalWrite(servo, LOW);
    trap_servo_pins[i] = servo;

    full[i] = false;
    fly_left[i] = false;
  }

  // INPUT is the default pin mode, but just to be clear
  pinMode(FLY_ENTRY_SENSOR, INPUT);
  pinMode(SORTER_PRESSURE_SENSOR, INPUT);
  
  sorter_sleeping = true;
  align_sorter();
  // for testing
  position_sorter(1);
  position_sorter(2);
  //

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
  /*
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
  */

  digitalWrite(VACUUM_VALVE, HIGH);
  delay(1000);
  digitalWrite(VACUUM_VALVE, LOW);
  delay(5000);
}
