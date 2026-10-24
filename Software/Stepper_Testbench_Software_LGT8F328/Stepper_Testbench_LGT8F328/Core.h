#pragma once
#include <stdint.h>
#include <stddef.h>

namespace tb {
constexpr uint16_t TickHz=10000, MaxPps=4000;
constexpr uint16_t timerCompare(uint32_t cpuHz) {return uint16_t(cpuHz/(8UL*TickHz)-1UL);}
constexpr uint16_t LeaseTicks=1000, DeadX=105, DeadY=95;
constexpr uint32_t SettingsMagic=0x55535442UL;
constexpr uint8_t SettingsVersion=2, MenuCount=9;
inline bool elapsed(uint32_t now,uint32_t since,uint32_t ms) { return uint32_t(now-since)>=ms; }

struct __attribute__((packed)) Profile {
  uint16_t fullSteps;
  uint8_t microIndex;
  uint16_t maxRpm,accelRpmPerSec,journeyDeg;
  uint8_t mode,hold,invert;
};
struct __attribute__((packed)) Settings {
  uint32_t magic;
  uint8_t version,selected;
  Profile p[2];
  uint16_t crc;
};
static_assert(sizeof(Settings)==32,"Persistent format changed: bump version");
extern const uint16_t FullStepOptions[4],RpmOptions[12],AccelOptions[9],DegreeOptions[8];
uint16_t crc16(const void *bytes,size_t length);
void defaults(Settings &s);
void seal(Settings &s);
bool validProfile(const Profile &p,uint8_t driver);
bool validSettings(const Settings &s);
bool migrateV1(const uint8_t *bytes,Settings &out);
uint8_t microsteps(const Settings &s);
uint8_t a4988Mask(uint8_t index);
uint32_t pulsesPerRev(const Settings &s);
uint32_t journeyPulses(const Settings &s);
uint16_t speedFromY(int raw,int center,const Settings &s,uint8_t &percent);
int8_t axis(int raw,int center,uint16_t dead);
bool neutral(int x,int y,int cx,int cy);
bool calibrationValid(int cx,int cy,int rangeX,int rangeY);
uint16_t cycle(const uint16_t *options,uint8_t count,uint16_t current,int8_t delta);

// Pure pulse scheduler, shared by the real Timer1 ISR and native tests.
// All access from the AVR foreground is enclosed in ATOMIC_BLOCK.
enum PulseEvent:uint8_t { Falling=1,Rising=2,LeaseExpired=4 };
struct PulseState {
  uint16_t rate=0,phase=0,lease=LeaseTicks;
  uint32_t remaining=0,emitted=0;
  bool high=false,finite=false,done=false,fault=false;
};
uint8_t pulseTick(volatile PulseState &p);
void pulseStop(volatile PulseState &p); // lets the current HIGH finish

enum ButtonEvent:uint8_t { Press=1,Double=2,Hold=4,Release=8 };
class Button {
 public:
  uint8_t update(uint32_t now,bool down,bool centered);
  void suppressHold() { eligible=false;handled=true;pending=false; }
  bool pressed() const { return stable; }
 private:
  bool raw=false,stable=false,eligible=false,handled=false,pending=false;
  uint32_t changed=0,downAt=0,firstDown=0;
};
class Repeat {
 public:
  bool update(uint32_t now,int8_t value);
  void reset() { last=0; }
 private:
  int8_t last=0;
  uint32_t since=0;
  bool repeating=false;
};
} // namespace tb

