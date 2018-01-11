
// TODO move most of the functions implemented here to a library
// and call that code. (not sure how to handle debug-flag-type settings?)

// TODO make sure these defines take priority over library ones (when test specific)
#if defined TEST_SHIFTREG || defined TEST_SHIFT_ALTERNATING
#define SHIFTREG_PERIOD_MS 50
#else
#define SHIFTREG_PERIOD_MS 0
#endif

// our isolation implementation inverts the logic
#define BYPASS_ISOLATION false

#if defined TEST_SHIFTREG || defined TEST_SHIFT_ALTERNATING
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
  
  // TODO include tests of behavior without settings pin states correctly initially?
  // TODO include a test enabling all combinations of these (at least that low disables)
  // TODO TODO are these not actually enabling output appropriately?
  // even after installing appropriate bypass cap, 
  // demux s.r. doesn't seem to send output high consistently. why?
  
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

  clear_reg();
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

#elif defined TEST_SHIFT_ALTERNATING
  Serial.println("shifting in a 1");
  digitalWrite(LED_BUILTIN, HIGH);
  shift_in(1);
  update_output();
  delay(INTERDIGIT_SHIFT_PERIOD_MS);

  Serial.println("shifting in a 0");
  digitalWrite(LED_BUILTIN, LOW);
  shift_in(0);
  update_output();
  delay(INTERDIGIT_SHIFT_PERIOD_MS);
  
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

#else
  #error One TEST_* needs to be #defined
#endif
}
