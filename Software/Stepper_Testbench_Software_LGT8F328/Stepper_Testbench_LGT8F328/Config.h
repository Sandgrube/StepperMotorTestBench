#pragma once
// Electrical and joystick options. Pin assignment matches enclosure R1.
// Keep TB_ENABLE_WIRED=0 unless ENA polarity has been checked on YOUR module.
#ifndef TB_ENABLE_WIRED
#define TB_ENABLE_WIRED 0
#endif
#ifndef TB_DISABLE_LEVEL
#define TB_DISABLE_LEVEL 1
#endif
#ifndef X_RIGHT_IS_HIGH
#define X_RIGHT_IS_HIGH 1
#endif
#ifndef Y_UP_IS_LOW
#define Y_UP_IS_LOW 1
#endif
#define FW_VERSION "2.1.0"

