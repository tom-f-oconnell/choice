
// TODO move most of the functions implemented here to a library
// and call that code. (not sure how to handle debug-flag-type settings?)

// uncomment one of these defines to select a test
#define TEST_ISOLATORS
//#define TEST_SHIFTREG
//#define TEST_SWITCH_SELECT (currently not implemented)
//#define TEST_SWITCH_SPEED
//#define TEST_SWITCH_SLOW
//#define TEST_ALL

#ifdef TEST_ISOLATORS
#define ISOLATED_PIN_TEST_PERIOD_MS 3000
#endif

#define SER   4
#define SRCLK 5
#define SRCLR 6
#define RCLK  7
#define FET_ENBL   8
#define DEMUX_ENBL 9 

#ifdef TEST_SHIFTREG
#define SHIFTREG_PERIOD_MS 50
#else
#define SHIFTREG_PERIOD_MS 0
#endif

// our isolation implementation inverts the logic
#define BYPASS_ISOLATION false

#ifdef TEST_SHIFTREG
#define SHIFT_REGISTER_BITS 16
#define INTERDIGIT_SHIFT_PERIOD_MS 500
#endif

#if defined TEST_SWITCH_SLOW || defined TEST_SWITCH_SPEED || defined TEST_ALL
#define MIN_DEMUX_PERIOD_MS 1
#endif

#if defined TEST_SWITCH_SLOW || defined TEST_SWITCH_SPEED 
#define SIGA 44
#define SIGB 45
#endif

#if defined TEST_SWITCH_SLOW || defined TEST_ALL
#define PERIOD_PER_CHANNEL_MS 5000
#endif

#ifdef TEST_ALL
#define FET_SWITCH_TO_SAMPLE_MS 1

/*
// TODO delete or redefine (i'm using those pins now)
#define ONE_L 2
#define ONE_R 8
#define TWO_L 9
#define TWO_R 10
*/
#endif

void clear_reg() {
  if (BYPASS_ISOLATION) {
    digitalWrite(SRCLR, LOW);
    digitalWrite(RCLK, LOW);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, HIGH);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, LOW);
    digitalWrite(SRCLR, HIGH);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
  } else {
    digitalWrite(SRCLR, HIGH);
    digitalWrite(RCLK, HIGH);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, LOW);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, HIGH);
    digitalWrite(SRCLR, LOW);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
  }
}

// takes HIGH (1) or LOW (0) as input
void shift_in(unsigned char value) {
  // logic should be inverted IF USING optoisolator
  // TODO if i'm not passing it in, maybe just use preprocessor conditional?
  if (BYPASS_ISOLATION) {
    digitalWrite(SRCLK, LOW);
  } else {
    digitalWrite(SRCLK, HIGH);
  }
#ifndef TEST_SWITCH_SPEED
  delay(SHIFTREG_PERIOD_MS);
#endif
  
  if (BYPASS_ISOLATION) {
    digitalWrite(SER, value);
  } else {
    digitalWrite(SER, 1 - value);
  }
#ifndef TEST_SWITCH_SPEED
  delay(SHIFTREG_PERIOD_MS);
#endif
  
  if (BYPASS_ISOLATION) {
    digitalWrite(SRCLK, HIGH);
  } else {
    digitalWrite(SRCLK, LOW);
  }
#ifndef TEST_SWITCH_SPEED
  delay(SHIFTREG_PERIOD_MS);
#endif
}

void update_output() {
  if (BYPASS_ISOLATION) {
    digitalWrite(RCLK, LOW);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, HIGH);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
  } else {
    digitalWrite(RCLK, HIGH);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
    digitalWrite(RCLK, LOW);
#ifndef TEST_SWITCH_SPEED
    delay(SHIFTREG_PERIOD_MS);
#endif
  }
}

// TODO store side information as another bit in a uchar / decode
// c should be between 0 and 7
// TODO include bypass_isolation flags in here (way to handle more uniformly?)
void select_input_channel(boolean left_side, unsigned char c) {
  // need to shift in starting with last value (QD; optional_demux_enable)
  // optional_demux_enable -> chan_select_B -> chan_select_A ->
  // demux_select_B -> demux_select_A
  clear_reg();
  
  // will always want to enable analog switch output
  shift_in(0);

  // "channels" are numbered from 1 to 8, so odd numbers come first
  // B (on CD4052B): 0 -> 0/1 (odd channels), 1 -> 2/3 (even channels)
  // TODO check this
  shift_in(1 - c % 2);
  
  // A (on CD4052B): 0 -> lower numbered choice given B (LEFT by my def), 1 -> higher (RIGHT)
  if (left_side) {
    shift_in(1);
  } else {
    shift_in(0);
  }

  // CD4556 (B): 0 -> Q0/Q1 (channels 1-2/3-4), 1 -> Q2/Q3 (channels 5-6/7-8)
  shift_in(c > 4);

  // CD4556 (A): 0 -> lower of above, 1 -> higher
  // TODO replace w/ one bitwise operation (at least verify)
  shift_in(c == 3 || c == 4 || c == 7 || c == 8);

  update_output();
}

// quickly switches between a HIGH and LOW signal to
// see how long it takes for the output to reflect the change
// TODO test w/ port manipulation rather than digitalwrite
// (to update shift registers and everything)
#ifdef TEST_SWITCH_SPEED
void test_analog_switch_speed() {
  // it seems that for short periods (< about 1ms)
  // the time it takes to switch depends somewhat on the channel
  // (such that it spends more time on ch0, for some reason.) digitalWrite?
  // (try CD4052B 0 HIGH, 1 LOW vs CD4052B 0 LOW, 1 HIGH to see) 
  select_input_channel(true, 1);
  delay(MIN_DEMUX_PERIOD_MS);
  select_input_channel(false, 1);
  delay(MIN_DEMUX_PERIOD_MS);
}
#endif

// slowly switch analog channels to verify visually on oscilloscope
// (switching slower should also be slightly more robust to failure)
#ifdef TEST_SWITCH_SLOW
void test_analog_switch_slow() {
  select_input_channel(true, 1);
  delay(MIN_DEMUX_PERIOD_MS);
  delay(PERIOD_PER_CHANNEL_MS);
  select_input_channel(false, 1);
  delay(MIN_DEMUX_PERIOD_MS);
  delay(PERIOD_PER_CHANNEL_MS);
}
#endif

#ifdef TEST_ALL
void report_reading() {
  int val;
  delay(FET_SWITCH_TO_SAMPLE_MS);
  // TODO maybe take multiple readings
  val = analogRead(A0);
  Serial.print("got reading ");
  Serial.print(val);
  Serial.println(" on A0\n");
}

// switches between the first two channels and reports single readings
// reading 1L/R with FETs as follows: L on, R on, both off, both off
void test_all() {
  Serial.println("selecting input channel 1L");
  Serial.println("turning on high voltage path for 1L");
  select_input_channel(true, 1);
  digitalWrite(ONE_L, HIGH);
  digitalWrite(ONE_R, LOW);
  report_reading();
  delay(MIN_DEMUX_PERIOD_MS);

  Serial.println("selecting input channel 1R");
  Serial.println("turning on high voltage path for 1R");
  select_input_channel(false, 1);
  delay(10);
  digitalWrite(ONE_L, LOW);
  digitalWrite(ONE_R, HIGH);
  report_reading();
  delay(MIN_DEMUX_PERIOD_MS);
  
  Serial.println("selecting input channel 1L");
  Serial.println("turning off high voltage paths to 1L and 1R");
  select_input_channel(true, 1);
  digitalWrite(ONE_L, LOW);
  digitalWrite(ONE_R, LOW);
  report_reading();
  delay(MIN_DEMUX_PERIOD_MS);

  Serial.println("selecting input channel 1R");
  select_input_channel(false, 1);
  report_reading();
  delay(MIN_DEMUX_PERIOD_MS);
  
  // TODO also test setting one pin high and reading other / 
  // addressing other channels / chips
}
#endif

void setup() {
  Serial.begin(9600);
  Serial.print("initializing... ");
  
  pinMode(SER, OUTPUT);
  pinMode(SRCLK, OUTPUT);
  pinMode(SRCLR, OUTPUT);
  pinMode(RCLK, OUTPUT);
  pinMode(FET_ENBL, OUTPUT);
  pinMode(DEMUX_ENBL, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  // LOW on output enable enables the shift register
  // and the isolation inverts the logic
  // TODO maybe include bypass isolation option

  // TODO include tests of behavior without settings pin states correctly initially?

#ifndef TEST_ISOLATORS
  digitalWrite(SER, HIGH);
  digitalWrite(SRCLK, HIGH);
  // sending this s.r. pin LOW clears the bits
  digitalWrite(SRCLR, LOW);
  digitalWrite(RCLK, HIGH);
  
  // TODO include a test enabling all combinations of these
  digitalWrite(FET_ENBL, HIGH);
  digitalWrite(DEMUX_ENBL, HIGH);
#endif

#ifdef TEST_ALL
  pinMode(ONE_L, OUTPUT);
  pinMode(ONE_R, OUTPUT);

  pinMode(A0, INPUT);
#endif

#if defined TEST_SWITCH_SPEED || defined TEST_ALL || defined TEST_SWITCH_SLOW
  // two different signals for verifying on oscilloscope
  // which channels of the analog switch are selected (assuming chip is working)
  // TODO can any arbitrary combination of pins be manipulated independently w/ PWM?
  pinMode(SIGA, OUTPUT);
  pinMode(SIGB, OUTPUT);
  //analogWrite(SIGA, 125);
  //analogWrite(SIGB, 125);
  digitalWrite(SIGA, LOW);
  digitalWrite(SIGB, HIGH);
#endif

#ifndef TEST_ISOLATORS
  clear_reg();
#endif
  Serial.println("done");
}

void loop() {
#ifdef TEST_SWITCH_SPEED
  test_analog_switch_speed();
  
#elif defined TEST_SWITCH_SLOW
  test_analog_switch_slow();
  
#elif defined TEST_SWITCH_SELECT
  #error TEST_SWITCH_SELECT needs implemented

#elif defined TEST_ALL
  test_all();
  
#elif defined TEST_SHIFTREG
  Serial.println("shifting in a 1");
  shift_in(1);
  update_output();
  delay(INTERDIGIT_SHIFT_PERIOD_MS);
  for (int i=0;i<SHIFT_REGISTER_BITS;i++) {
    Serial.println("shifting in a 0");
    shift_in(0);
    update_output();
    delay(INTERDIGIT_SHIFT_PERIOD_MS);
//    if (i == 5) {
//      clear_reg();
//      break;
//    }
  }
#elif defined TEST_ISOLATORS

  digitalWrite(SER, HIGH);
  digitalWrite(SRCLK, HIGH);
  digitalWrite(SRCLR, HIGH);
  digitalWrite(RCLK, HIGH);
  digitalWrite(FET_ENBL, HIGH);
  digitalWrite(DEMUX_ENBL, HIGH);
  digitalWrite(LED_BUILTIN, LOW);
  delay(ISOLATED_PIN_TEST_PERIOD_MS);
  
  digitalWrite(SER, LOW);
  digitalWrite(SRCLK, LOW);
  digitalWrite(SRCLR, LOW);
  digitalWrite(RCLK, LOW);
  digitalWrite(FET_ENBL, LOW);
  digitalWrite(DEMUX_ENBL, LOW);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(ISOLATED_PIN_TEST_PERIOD_MS);
  
#else
  #error One TEST_* needs to be #defined
#endif
}
