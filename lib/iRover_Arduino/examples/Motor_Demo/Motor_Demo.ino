#include <IROVER.h>
void setup() {
  init(0x48); // set iKB1z address 0x48
}
void loop() {
  // Motor 1 & 2 Forward power 50%
  motor(1, 50);
  motor(2, 50);
  // Wait 1 Sec.
  delay(1000);
  // motor Stop
  motor_stop(ALL);
  // Motor 1 & 2 Forward power 50%
  fd(50);
  // Wait 1 Sec.
  delay(1000);
  // motor Stop
  ao();
  // Motor 1 & 2 Backward power 50%
  bk(50);
  // Wait 1 Sec.
  delay(1000);
  // motor Stop
  ao();
  // Motor 1 Backward  2 Forward power 50%
  sl(50);
  // Wait 1 Sec.
  delay(1000);
  // motor Stop
  ao();
  // Motor 1 Forward  2 Backward power 50%
  sr(50);
  // Wait 1 Sec.
  delay(1000);
  // motor Stop
  ao();
  // Motor 1 to 0 and  2 Forward power 50%
  tl(50);
  // Wait 1 Sec.
  delay(1000);
  // motor Stop
  ao();
  // Motor 1 Forward power 50% and 2 to 0
  tr(50);
  // Wait 1 Sec.
  delay(1000);
  // motor Stop
  ao();
}
