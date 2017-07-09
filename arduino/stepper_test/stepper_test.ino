
#define STEP_PIN1 53
#define SLEEP_PIN1 51
#define STEP_PIN2 49
#define SLEEP_PIN2 47

// l to r on shield : green,black.red,blue

void pulse(int pin) {
  digitalWrite(pin, HIGH);
  delayMicroseconds(2);
  digitalWrite(pin, LOW);
  delay(1);
}

void tenth() {
  for (int i=0;i<160;i++) {
    pulse1();
    delay(20);
  }
}

void one_rev() {
  for (int i=0;i<10;i++) {
    tenth();
    delay(2000);
  }
}

void pulse1() {
  pulse(STEP_PIN1);
}

void pulse2() {
  pulse(STEP_PIN2);
}

boolean rotate = false;
boolean sleeping = true;

void unsleep() {
  if (sleeping) {
    digitalWrite(SLEEP_PIN1, HIGH);
    sleeping = false;
  }
}

void resleep() {
  if (!sleeping) {
    digitalWrite(SLEEP_PIN1, LOW);
    sleeping = true;
  }
}

void serialEvent(){
  char in = (char) Serial.read();
  if (in == 's') {
    unsleep();
    delay(1000);
    for (int i=0;i<10;i++) {
      pulse1();
      delay(20);
    }
    delay(1000);
    resleep();
  } else if (in == 'r') {
    rotate = true;
  } else if (in == 'e') {
    rotate = false;
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(SLEEP_PIN1, OUTPUT);
  pinMode(STEP_PIN1, OUTPUT);
  digitalWrite(SLEEP_PIN1, HIGH);
  digitalWrite(STEP_PIN1, LOW);
}

unsigned long last = 0;

void loop() {
  if (rotate) {
    digitalWrite(SLEEP_PIN1, HIGH);
    if (millis() > last + 2000) {
      tenth();
      last = millis();
    }
  } else {
    digitalWrite(SLEEP_PIN1, LOW);
  }
  //Serial.println(analogRead(A0));
}
