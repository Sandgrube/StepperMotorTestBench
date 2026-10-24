/*
  Stepper Testbench 2.1.0 — LGT8F328P/D, 16 or 32 MHz, LQFP32/48 pin harness.
  Open this file with ALL companion files in the same sketch folder.
  Library: hd44780 by Bill Perry 1.3.2; board package: lgt8fx 2.0.7.
  Pin/electrical options: Config.h. Wiring and commissioning: ../README.md.
  Timer1 is exclusive. No extra controls or electronics are needed.
*/
#include "App.h"
void setup() { testbenchSetup(); }
void loop() { testbenchLoop(); }

