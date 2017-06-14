#include <Servo.h>

#define SERVO_WAIT_TIME_MS 500
#define TRAP_VALVE_TIME_MS 6000
#define EGRESS_VALVE_TIME_MS 5000
#define NUM_PINS 20
#define NUM_TRAPS 1

#define ENTRY_CONTROL_PIN 2
#define EGRESS_SLIDER_PIN 3
#define EGRESS_VALVE_PIN 4
#define FIRST_TRAP_PIN 5
#define INTERRUPT_PIN A0

// (degrees)
#define BLOCKED 130
#define OPEN 140

#define EXPERIMENT 132
#define EGRESS 147

// head attached in TRAP_READY position after servo is written to 180 degrees.
#define TRAP_READY 160
#define TRAP_OPEN 93

// 1 servo to control slider to vacuum flies out
// 1 servo to control flies entering system from vial
const int NUM_SERVOS = NUM_TRAPS + 2;

Servo servos[NUM_PINS];

int TEST_DELAY = 2000;

// pins these servos are on
unsigned char egress_slider = 2;
unsigned char trap1 = 3;
int trap_servo_pins[NUM_TRAPS];

// will likely use a shift register based solution in future
int trap_valve_pins[NUM_TRAPS];

// TODO make timer based w/ global update if necessary
void move_servo(int pin, int deg) {
  Servo s = servos[pin];
  s.attach(pin);
  s.write(deg);
  delay(SERVO_WAIT_TIME_MS);
  s.detach();
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
}

// TODO maybe change design such that i can suck individual flies out later?
// way to do it w/o changing design?
void end_experiment() {
  move_servo(EGRESS_SLIDER_PIN, EGRESS);
  // TODO use rotary valve or something to limit available vacuum pressure
  // to one channel at a time, if necessary to remove flies reliably
  digitalWrite(EGRESS_VALVE_PIN, HIGH);
  delay(EGRESS_VALVE_TIME_MS);
  digitalWrite(EGRESS_VALVE_PIN, LOW);
}

boolean fly_detected() {
  // TODO TODO TODO
  // may have to debounce / filter somehow
  //return digitalRead(INTERRUPT_PIN);
  return true;
}

void wait_for_fly() {
  while (!fly_detected()) { ;}
}

void let_fly_in(int i) {
  //move_servo(ENTRY_CONTROL_PIN, OPEN);
  move_servo(trap_servo_pins[i], TRAP_READY);
  wait_for_fly();
  // apply vacuum to this trap
  digitalWrite(trap_valve_pins[i], HIGH);
  delay(TRAP_VALVE_TIME_MS);
  digitalWrite(trap_valve_pins[i], LOW);
  // TODO maybe put this above vacuum pulse?
  //move_servo(ENTRY_CONTROL_PIN, BLOCKED);
  
  // could also do this for all traps at the same time, and first
  // put the trap in an intermediate, sealed, position
  move_servo(trap_servo_pins[i], TRAP_OPEN);
}

void setup() {
  // make sure all pins that are supposed to be outputs are set here
  pinMode(ENTRY_CONTROL_PIN, OUTPUT);
  pinMode(EGRESS_SLIDER_PIN, OUTPUT);
  pinMode(EGRESS_VALVE_PIN, OUTPUT);

  for (int i=0;i<NUM_TRAPS;i++) {
    int servo_pin = FIRST_TRAP_PIN + i;
    pinMode(servo_pin, OUTPUT);
    trap_servo_pins[i] = servo_pin;

    int valve_pin = FIRST_TRAP_PIN + NUM_TRAPS + i;
    pinMode(valve_pin, OUTPUT);
    trap_valve_pins[i] = valve_pin;
  }

  // this is the default, but just to be clear
  pinMode(INTERRUPT_PIN, INPUT);
  //move_all_trap_servos_to_145();
  ready_experiment();
}

/* TODO:
-how to coordinate experiment state w/ ROS nodes (when to suck flies in/out,
 ,etc)?
-is this also controlling shock? may need more pins then? (maybe just 1, or shift)
*/

void loop() {
  //ready_experiment();
  let_fly_in(0);
  delay(2000);
  //end_experiment();
}
