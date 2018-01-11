
// TODO quotes here?
#include <multishock.h>

#define ISOLATED_PIN_TEST_PERIOD_MS 3000

void setup() {
  // sets pinMode and initial state of all pins #defined in multishock.h
  // (the pins referenced below)
  ms_init();
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(SER, HIGH);
  digitalWrite(SRCLK, HIGH);
  digitalWrite(SRCLR, HIGH);
  digitalWrite(RCLK, HIGH);
  digitalWrite(FET_ENBL, HIGH);
  digitalWrite(DEMUX_ENBL, HIGH);

  // led pin flashed w/ opposite logic, to more easily think of the 
  // inversion by the optoisolators
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
}
