
#define SER   3
#define SRCLK 4
#define SRCLR 5
#define RCLK  6
#define ENBL  7
#define WAIT_MS 1
#define SHIFT_PERIOD_MS 500
#define DEMUX_WAIT_MS 5000
#define PRE_SAMPLE_WAIT_MS 1

#define ONE_L 2
#define ONE_R 8
#define TWO_L 9
#define TWO_R 10

// our isolation implementation inverts the logic
#define BYPASS_ISOLATION false

#define SIGA 44
#define SIGB 45

int val = 0;

void clear_reg() {
  if (BYPASS_ISOLATION) {
    digitalWrite(SRCLR, LOW);
    digitalWrite(RCLK, LOW);
    delay(WAIT_MS);
    digitalWrite(RCLK, HIGH);
    delay(WAIT_MS);
    digitalWrite(RCLK, LOW);
    digitalWrite(SRCLR, HIGH);
    delay(WAIT_MS);
  } else {
    digitalWrite(SRCLR, HIGH);
    digitalWrite(RCLK, HIGH);
    delay(WAIT_MS);
    digitalWrite(RCLK, LOW);
    delay(WAIT_MS);
    digitalWrite(RCLK, HIGH);
    digitalWrite(SRCLR, LOW);
    delay(WAIT_MS);
  }
}

// takes HIGH (1) or LOW (0) as input
void shift_in(unsigned char value) {
  // logic should be inverted IF USING optoisolator
  if (BYPASS_ISOLATION) {
    digitalWrite(SRCLK, LOW);
  } else {
    digitalWrite(SRCLK, HIGH);
  }
  delay(WAIT_MS);
  
  if (BYPASS_ISOLATION) {
    digitalWrite(SER, value);
  } else {
    digitalWrite(SER, 1 - value);
  }
  delay(WAIT_MS);
  
  if (BYPASS_ISOLATION) {
    digitalWrite(SRCLK, HIGH);
  } else {
    digitalWrite(SRCLK, LOW);
  }
  delay(WAIT_MS);
}

void update_output() {
  if (BYPASS_ISOLATION) {
    digitalWrite(RCLK, LOW);
    delay(WAIT_MS);
    digitalWrite(RCLK, HIGH);
    delay(WAIT_MS);
  } else {
    digitalWrite(RCLK, HIGH);
    delay(WAIT_MS);
    digitalWrite(RCLK, LOW);
    delay(WAIT_MS);
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

void setup() {
  Serial.begin(9600);
  Serial.print("initializing... ");
  
  pinMode(SER, OUTPUT);
  pinMode(SRCLK, OUTPUT);
  pinMode(SRCLR, OUTPUT);
  pinMode(RCLK, OUTPUT);
  pinMode(ENBL, OUTPUT);

  pinMode(ONE_L, OUTPUT);
  pinMode(ONE_R, OUTPUT);

  pinMode(A0, INPUT);

  // two different PWM signals for verifying on oscilloscope
  // which channels of the analog switch are selected (assuming chip is working)
  // TODO can any arbitrary combination of pins be manipulated independently w/ PWM?
  pinMode(SIGA, OUTPUT);
  pinMode(SIGB, OUTPUT);
  analogWrite(SIGA, 240);
  analogWrite(SIGB, 125);

  clear_reg();
  Serial.println("done");
}

void report_reading() {
  delay(PRE_SAMPLE_WAIT_MS);
  // TODO maybe take multiple readings
  val = analogRead(A0);
  Serial.print("got reading ");
  Serial.print(val);
  Serial.println(" on A0\n");
}

void loop() {
  Serial.println("selecting input channel 1L");
  Serial.println("turning on high voltage path for 1L");
  select_input_channel(true, 1);
  digitalWrite(ONE_L, HIGH);
  digitalWrite(ONE_R, LOW);
  report_reading();
  delay(DEMUX_WAIT_MS);

  Serial.println("selecting input channel 1R");
  Serial.println("turning on high voltage path for 1R");
  select_input_channel(false, 1);
  digitalWrite(ONE_L, LOW);
  digitalWrite(ONE_R, HIGH);
  report_reading();
  delay(DEMUX_WAIT_MS);

  Serial.println("selecting input channel 1L");
  Serial.println("turning off high voltage paths to 1L and 1R");
  select_input_channel(true, 1);
  digitalWrite(ONE_L, LOW);
  digitalWrite(ONE_R, LOW);
  report_reading();
  delay(DEMUX_WAIT_MS);

  Serial.println("selecting input channel 1R");
  select_input_channel(false, 1);
  report_reading();
  delay(DEMUX_WAIT_MS);

  // TODO also test setting one pin high and reading other / 
  // addressing other channels / chips
  /*
  //clear_reg();
  shift_in(1);
  update_output();
  delay(SHIFT_PERIOD_MS);
  for (int i=0;i<8;i++) {
    shift_in(0);
    update_output();
    delay(SHIFT_PERIOD_MS);
//    if (i == 5) {
//      clear_reg();
//      break;
//    }
  }
  */
}
