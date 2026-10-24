/* Stepper Testbench 2.1.0 — generated single-file edition.
   LGT8F328P/D at 16/32 MHz; lgt8fx 2.0.7 + hd44780 1.3.2.
   Edit electrical options in the Config.h section below.
   Modular editable sources, tests and wiring manual are in the complete ZIP.
   Regenerate this file: python tools/make_single_file.py
*/
#include <Arduino.h>

// ===== Config.h =====
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


// ===== Core.h =====
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


// ===== Control.h =====
namespace tb {
struct Snapshot {uint32_t remaining,emitted;uint16_t rate;bool high,done,stale;};
class MotorPort {
 public:
  virtual void stop()=0;
  virtual void rate(uint16_t pps)=0;
  virtual void finite(uint32_t count)=0;
  virtual Snapshot snapshot()=0;
  virtual void configure(uint8_t driver,uint8_t microIndex)=0;
  virtual void direction(int8_t dir,bool invert)=0;
  virtual void power(bool on)=0;
};
enum Fault:uint8_t {NoFault,LcdFault,JoystickFault,LoopFault,BoardFault,StorageFault};
class Control {
 public:
  explicit Control(MotorPort &port):motor(port) {defaults(settings);}
  Settings settings;
  bool armed=false,menu=false,journeyRunning=false,saveRequested=false;
  bool dirty=true,releaseToRun=false,journeyNeutralRequired=true;
  uint8_t page=0,throttle=0;
  int8_t stick=0;
  int centerX=512,centerY=512;
  Fault fault=NoFault;
  float motionPps=0;
  void begin(uint32_t now,int cx,int cy,bool goodCalibration);
  void update(uint32_t now,int rawX,int rawY,bool buttonDown);
  void stop();
  void fail(Fault why);
  void applyConfiguration(uint32_t now);
  bool powered()const{return powerOn;}
 private:
  MotorPort &motor;
  Button button;
  Repeat navX,navY;
  bool powerOn=false;
  int8_t currentDir=1;
  uint32_t lastControl=0,dirAt=0,powerAt=0;
  uint16_t cruise=0;
  void change(int8_t delta);
  void setPower(bool on,uint32_t now);
  bool prepare(int8_t dir,uint32_t now);
  void move(uint32_t now,int x,int y);
};
} // namespace tb


// ===== Ui.h =====
namespace tb { void render(const Control &c,const Snapshot &s,char rows[2][17]); }


// ===== App.h =====
void testbenchSetup();
void testbenchLoop();


// ===== Core.cpp =====
#include <string.h>

namespace tb {
const uint16_t FullStepOptions[4]={48,100,200,400};
const uint16_t RpmOptions[12]={3,5,10,15,20,30,45,60,90,120,180,240};
const uint16_t AccelOptions[9]={10,20,40,60,90,120,180,240,360};
const uint16_t DegreeOptions[8]={15,30,45,90,180,360,720,1440};
static const uint8_t MicroTB[6]={1,2,4,8,16,32},MicroA[5]={1,2,4,8,16};
static bool contains(const uint16_t *a,uint8_t n,uint16_t v) {
  for(uint8_t i=0;i<n;++i) if(a[i]==v) return true;
  return false;
}
uint16_t crc16(const void *bytes,size_t length) {
  const uint8_t *p=static_cast<const uint8_t *>(bytes);
  uint16_t crc=0xffff;
  for(size_t i=0;i<length;++i) {
    crc^=uint16_t(p[i])<<8;
    for(uint8_t b=0;b<8;++b) crc=(crc&0x8000)?uint16_t((crc<<1)^0x1021):uint16_t(crc<<1);
  }
  return crc;
}
void seal(Settings &s) { s.magic=SettingsMagic;s.version=SettingsVersion;s.crc=crc16(&s,offsetof(Settings,crc)); }
void defaults(Settings &s) {
  memset(&s,0,sizeof(s));
  s.p[0]={200,3,15,60,180,0,0,0};
  s.p[1]=s.p[0];
  seal(s);
}
bool validProfile(const Profile &p,uint8_t driver) {
  return driver<2 && contains(FullStepOptions,4,p.fullSteps) && p.microIndex<(driver?5:6)
    && contains(RpmOptions,12,p.maxRpm) && contains(AccelOptions,9,p.accelRpmPerSec)
    && contains(DegreeOptions,8,p.journeyDeg) && p.mode<2 && p.hold<2 && p.invert<2;
}
bool validSettings(const Settings &s) {
  return s.magic==SettingsMagic && s.version==SettingsVersion && s.selected<2
    && s.crc==crc16(&s,offsetof(Settings,crc)) && validProfile(s.p[0],0) && validProfile(s.p[1],1);
}
bool migrateV1(const uint8_t *bytes,Settings &out) {
  struct __attribute__((packed)) OldProfile {uint16_t fullSteps;uint8_t microIndex;uint16_t maxRpm,accel,deg;uint8_t mode,hold;};
  struct __attribute__((packed)) OldSettings {uint32_t magic;uint8_t version,selected;OldProfile p[2];uint16_t crc;};
  static_assert(sizeof(OldSettings)==30,"Legacy format");
  OldSettings old;memcpy(&old,bytes,sizeof(old));
  if(old.magic!=SettingsMagic || old.version!=1 || old.selected>1 || old.crc!=crc16(bytes,28)) return false;
  defaults(out);out.selected=old.selected;
  for(uint8_t i=0;i<2;++i) {
    const OldProfile &p=old.p[i];
    out.p[i]={p.fullSteps,p.microIndex,p.maxRpm,p.accel,p.deg,p.mode,p.hold,0};
    if(!validProfile(out.p[i],i)) return false;
  }
  seal(out);return true;
}
uint8_t microsteps(const Settings &s) { return s.selected?MicroA[s.p[1].microIndex]:MicroTB[s.p[0].microIndex]; }
uint8_t a4988Mask(uint8_t index) { const uint8_t masks[5]={0,1,2,3,7};return index<5?masks[index]:0; }
uint32_t pulsesPerRev(const Settings &s) { return uint32_t(s.p[s.selected].fullSteps)*microsteps(s); }
uint32_t journeyPulses(const Settings &s) { return (uint32_t(s.p[s.selected].journeyDeg)*pulsesPerRev(s)+180UL)/360UL; }
int8_t axis(int raw,int center,uint16_t dead) { return raw>center+int(dead)?1:raw<center-int(dead)?-1:0; }
bool neutral(int x,int y,int cx,int cy) { return axis(x,cx,DeadX)==0 && axis(y,cy,DeadY)==0; }
bool calibrationValid(int cx,int cy,int rx,int ry) {return cx>=350 && cx<=674 && cy>=350 && cy<=674 && rx<=40 && ry<=40;}
uint16_t speedFromY(int raw,int center,const Settings &s,uint8_t &percent) {
  int delta=raw-center;int magnitude=delta<0?-delta:delta;
  if(magnitude<=int(DeadY)) {percent=0;return 0;}
  int span=(delta<0?center:1023-center)-DeadY;
  if(span<=0) {percent=0;return 0;}
  int amount=magnitude-DeadY;
  uint32_t permille=uint32_t(amount)*1000UL/uint16_t(span);
  if(permille>1000)permille=1000;
  percent=uint8_t((permille+5)/10);
  // Physical RPM: 1 to profile maximum. Use 64-bit intermediate only in foreground.
  uint32_t rpmMilli=1000UL+uint32_t(s.p[s.selected].maxRpm-1)*permille;
  uint32_t pps=uint32_t((uint64_t(rpmMilli)*pulsesPerRev(s)+30000UL)/60000UL);
  return pps>MaxPps?MaxPps:uint16_t(pps?pps:1);
}
uint16_t cycle(const uint16_t *options,uint8_t count,uint16_t current,int8_t delta) {
  uint8_t at=0;for(uint8_t i=0;i<count;++i)if(options[i]==current){at=i;break;}
  return options[(at+count+(delta>0?1:count-1))%count];
}
void pulseStop(volatile PulseState &p) {
  p.rate=0;p.phase=0;p.finite=false;p.remaining=0;p.done=false;
  // p.high is intentionally retained; the next tick completes the pulse.
}
uint8_t pulseTick(volatile PulseState &p) {
  uint8_t event=0;const bool wasHigh=p.high;
  if(wasHigh) {p.high=false;event|=Falling;}
  if(!p.fault) {
    if(p.lease) --p.lease;
    else {p.fault=true;pulseStop(p);event|=LeaseExpired;}
  }
  if(p.fault || p.done || !p.rate) return event;
  p.phase=uint16_t(p.phase+p.rate);
  if(!wasHigh && p.phase>=TickHz) {
    p.phase=uint16_t(p.phase-TickHz);p.high=true;++p.emitted;event|=Rising;
    if(p.finite) {
      if(p.remaining) --p.remaining;
      if(!p.remaining) {p.rate=0;p.finite=false;p.done=true;}
    }
  }
  return event;
}
uint8_t Button::update(uint32_t now,bool down,bool centered) {
  uint8_t event=0;
  if(down!=raw) {raw=down;changed=now;}
  if(stable && !centered) eligible=false;
  if(pending && elapsed(now,firstDown,350)) pending=false;
  if(raw!=stable && elapsed(now,changed,25)) {
    stable=raw;
    if(stable) {
      event|=Press;downAt=now;eligible=centered;handled=false;
      if(pending && !elapsed(now,firstDown,350)) {event|=Double;handled=true;eligible=false;pending=false;}
    } else {
      event|=Release;
      if(!handled && !elapsed(now,downAt,350)) {pending=true;firstDown=downAt;}
      else pending=false;
    }
  }
  if(stable && eligible && !handled && elapsed(now,downAt,1100)) {
    event|=Hold;handled=true;pending=false;
  }
  return event;
}
bool Repeat::update(uint32_t now,int8_t value) {
  if(!value) {last=0;repeating=false;return false;}
  if(value!=last) {last=value;since=now;repeating=false;return true;}
  if(elapsed(now,since,repeating?190:420)) {since=now;repeating=true;return true;}
  return false;
}
} // namespace tb


// ===== Control.cpp =====
#include <math.h>

namespace tb {
void Control::begin(uint32_t now,int cx,int cy,bool good) {
  centerX=cx;centerY=cy;lastControl=now;
  stop();applyConfiguration(now);
  if(!good)fail(JoystickFault);
}
void Control::stop() {
  motor.stop();armed=false;journeyRunning=false;motionPps=0;
  journeyNeutralRequired=true;releaseToRun=true;
  // Finish any existing HIGH before the foreground disables power.
  if(!motor.snapshot().high) {motor.power(false);powerOn=false;}
  dirty=true;
}
void Control::fail(Fault why) {stop();fault=why;menu=false;button.suppressHold();}
void Control::applyConfiguration(uint32_t now) {
  motor.stop();motor.power(false);powerOn=false;
  motor.configure(settings.selected,settings.p[1].microIndex);
  currentDir=1;motor.direction(currentDir,settings.p[settings.selected].invert);
  dirAt=now;dirty=true;
}
void Control::setPower(bool on,uint32_t now) {
  if(on==powerOn)return;
  motor.power(on);powerOn=on;powerAt=now;
}
bool Control::prepare(int8_t dir,uint32_t now) {
  Snapshot s=motor.snapshot();
  if(dir!=currentDir) {
    if(motionPps>0.5f || s.high || s.rate)return false;
    motor.stop();currentDir=dir;
    motor.direction(dir,settings.p[settings.selected].invert);dirAt=now;
  }
  setPower(true,now);
  return elapsed(now,dirAt,5) && elapsed(now,powerAt,5);
}
void Control::change(int8_t delta) {
  Profile &p=settings.p[settings.selected];
  switch(page) {
    case 0:settings.selected^=1;break;
    case 1:p.mode^=1;break;
    case 2:p.fullSteps=cycle(FullStepOptions,4,p.fullSteps,delta);break;
    case 3:{uint8_t n=settings.selected?5:6;p.microIndex=(p.microIndex+n+(delta>0?1:n-1))%n;break;}
    case 4:p.maxRpm=cycle(RpmOptions,12,p.maxRpm,delta);break;
    case 5:p.accelRpmPerSec=cycle(AccelOptions,9,p.accelRpmPerSec,delta);break;
    case 6:p.journeyDeg=cycle(DegreeOptions,8,p.journeyDeg,delta);break;
    case 7:
#if TB_ENABLE_WIRED
      p.hold^=1;
#else
      if(settings.selected)p.hold^=1;
#endif
      break;
    case 8:p.invert^=1;break;
  }
  dirty=true;
}
void Control::update(uint32_t now,int rawX,int rawY,bool down) {
  if(fault!=NoFault) {motor.stop();if(!motor.snapshot().high)setPower(false,now);return;}
  if(motor.snapshot().stale) {fail(LoopFault);return;}
  if(!armed && powerOn && !motor.snapshot().high)setPower(false,now);
  bool centered=neutral(rawX,rawY,centerX,centerY);
  uint8_t event=button.update(now,down,centered);
  if(event&Press) {
    if(menu) {
      menu=false;stop();applyConfiguration(now);saveRequested=true;button.suppressHold();
    } else {
      stop();
      if(event&Double) {menu=true;page=0;navX.reset();navY.reset();button.suppressHold();}
    }
  }
  if((event&Hold) && !menu) {armed=true;releaseToRun=true;dirty=true;}
  if(!button.pressed() && !down) releaseToRun=false;
  if(menu) {
    // A diagonal navigation gesture changes the page only, preventing accidental edits.
    int8_t y=axis(rawY,centerY,235);
#if !Y_UP_IS_LOW
    y=-y;
#endif
    if(navY.update(now,y)) {page=(page+MenuCount+(y<0?MenuCount-1:1))%MenuCount;navX.reset();dirty=true;}
    if(!y) {int8_t x=axis(rawX,centerX,235);
#if !X_RIGHT_IS_HIGH
      x=-x;
#endif
      if(navX.update(now,x))change(x);
    } else navX.reset();
    return;
  }
  if(!elapsed(now,lastControl,5))return;
  move(now,rawX,rawY);
}
void Control::move(uint32_t now,int x,int y) {
  float dt=uint32_t(now-lastControl)*0.001f;lastControl=now;
  if(dt>0.025f)dt=0.025f;
  stick=axis(x,centerX,DeadX);
#if !X_RIGHT_IS_HIGH
  stick=-stick;
#endif
  uint16_t request=speedFromY(y,centerY,settings,throttle);
  Snapshot snap=motor.snapshot();
  if(!armed || releaseToRun) {
    motor.stop();motionPps=0;
    if(!snap.high)setPower(false,now);
    return;
  }
  const Profile &p=settings.p[settings.selected];
  if(journeyRunning && snap.done && !snap.high) {
    motor.stop();journeyRunning=false;motionPps=0;journeyNeutralRequired=true;
    setPower(p.hold,now);dirty=true;return;
  }
  float target=0;
  float accel=float(p.accelRpmPerSec)*pulsesPerRev(settings)/60.0f;
  if(p.mode) {
    if(!journeyRunning && !stick)journeyNeutralRequired=false;
    if(!journeyRunning && !journeyNeutralRequired && stick && request) {
      if(prepare(stick,now)) {
        motor.stop();motor.finite(journeyPulses(settings));journeyRunning=true;
        journeyNeutralRequired=true;cruise=request;motionPps=0;dirty=true;
      }
    }
    if(journeyRunning) {
      snap=motor.snapshot();
      // Reserve one step and 20ms for sampled control + pulse quantisation.
      float distance=snap.remaining>1?float(snap.remaining-1):0;
      float margin=accel*0.020f;
      float limit=sqrtf(margin*margin+2*accel*distance)-margin;
      if(limit<5 && snap.remaining)limit=5;
      target=limit<float(cruise)?limit:float(cruise);
      if(!snap.remaining)target=0;
    }
  } else if(stick && request) {
    if(prepare(stick,now))target=request;
  }
  float advance=accel*dt;
  if(motionPps<target) {motionPps+=advance;if(motionPps>target)motionPps=target;}
  else if(motionPps>target) {motionPps-=advance;if(motionPps<target)motionPps=target;}
  // Preserve fractional increments at small steps/rev and low acceleration.
  if(target==0 && motionPps<0.5f)motionPps=0;
  uint16_t pps=uint16_t(motionPps+0.5f);
  if(pps>MaxPps)pps=MaxPps;
  // A completed finite block must never be restarted by a foreground rate update.
  if(journeyRunning && motor.snapshot().done)pps=0;
  motor.rate(pps);
  bool waitingStart=stick && request && (!p.mode || !journeyNeutralRequired);
  bool needPower=pps || journeyRunning || waitingStart || p.hold;
  // Keep power during an active HIGH; release after the pulse has ended.
  if(!needPower && !motor.snapshot().high)setPower(false,now);
  else if(needPower)setPower(true,now);
}
} // namespace tb


// ===== Ui.cpp =====
#include <stdio.h>
#include <string.h>

namespace tb {
static void pad(char *s) {
  size_t n=strlen(s);while(n<16)s[n++]=' ';s[16]=0;
}
void render(const Control &c,const Snapshot &s,char rows[2][17]) {
  rows[0][0]=rows[1][0]=0;
  const Profile &p=c.settings.p[c.settings.selected];
  if(c.fault!=NoFault) {
    const char *why=c.fault==LcdFault?"LCD/I2C":c.fault==JoystickFault?"Joystick":c.fault==BoardFault?"Boardpins":c.fault==StorageFault?"Speicher":"Loop-Zeit";
    snprintf(rows[0],17,"FEHLER %s",why);snprintf(rows[1],17,"Reset / USB neu");
  } else if(c.menu) {
    const char *labels[MenuCount]={"Treiber","Modus","Vollschr","Mikro","Max RPM","Beschl","Weg Grad","Halten","Richtung"};
    snprintf(rows[0],17,"%u/9 %s",c.page+1,labels[c.page]);
    switch(c.page) {
      case 0:snprintf(rows[1],17,"> %s",c.settings.selected?"A4988":"TB6600");break;
      case 1:snprintf(rows[1],17,"> %s",p.mode?"Fahrt":"Dauerlauf");break;
      case 2:snprintf(rows[1],17,"> %u / U",p.fullSteps);break;
      case 3:snprintf(rows[1],17,"> 1/%u %s",microsteps(c.settings),c.settings.selected?"AUTO":"DIP!");break;
      case 4:snprintf(rows[1],17,"> %u rpm",p.maxRpm);break;
      case 5:snprintf(rows[1],17,"> %u rpm/s",p.accelRpmPerSec);break;
      case 6:snprintf(rows[1],17,"> %u Grad",p.journeyDeg);break;
      case 7:
#if TB_ENABLE_WIRED
        snprintf(rows[1],17,"> %s",p.hold?"Ein":"Aus");
#else
        snprintf(rows[1],17,"> %s",c.settings.selected?(p.hold?"Ein":"Aus"):"TB ENA offen");
#endif
        break;
      case 8:snprintf(rows[1],17,"> %s",p.invert?"Invertiert":"Normal");break;
    }
  } else {
    const char *state=!c.armed?"LOCK":c.journeyRunning||s.rate?"RUN":"ARM";
    snprintf(rows[0],17,"%-6s %c %s",c.settings.selected?"A4988":"TB6600",p.mode?'J':'C',state);
    if(!c.armed)snprintf(rows[1],17,"Halt1.1s 2xMenue");
    else if(c.releaseToRun)snprintf(rows[1],17,"Taste loslassen");
    else if(c.journeyRunning) {
      uint16_t left=s.remaining>65535UL?65535:uint16_t(s.remaining);
      snprintf(rows[1],17,"Rest:%u Pulse",unsigned(left));
    }
    else if(s.rate) {
      uint16_t rpm=uint16_t((uint32_t(s.rate)*60UL+pulsesPerRev(c.settings)/2)/pulsesPerRev(c.settings));
      snprintf(rows[1],17,"%c %3urpm %3u%%",c.stick<0?'<':'>',rpm,c.throttle);
    } else snprintf(rows[1],17,"X:Richt Y:Tempo");
  }
  pad(rows[0]);pad(rows[1]);
}
} // namespace tb


// ===== App.cpp =====
#include <Arduino.h>
#include <Wire.h>
#include <EEPROM.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>
#include <avr/interrupt.h>
#include <util/atomic.h>
#include <string.h>

#if !defined(__LGT8F__) || (!defined(__LGT8FX8P__) && !defined(__LGT8FX8E__)) || (F_CPU!=16000000UL && F_CPU!=32000000UL)
#error "Select LGT8fx LGT8F328 at 16/32 MHz. Arduino Uno is the wrong core for this hardware."
#endif
#if defined(__LGT8F_SSOP20__)
#error "The SSOP20 pin mapping is not supported by this testbench harness. Use a verified LQFP32/48 board."
#endif
#if defined(__LGT8F__) && !defined(lgt_eeprom_free_space_per_1KB_page)
#error "Use the E2PROM/EEPROM library bundled with lgt8fx, not the Arduino AVR EEPROM library."
#endif
static_assert(F_CPU%(8UL*tb::TickHz)==0,"Timer1 tick requires an integer compare value");

namespace {
constexpr uint8_t JoyX=A0,JoyY=A1,JoySW=2;
constexpr uint8_t TbStep=3,TbDir=4,TbOff=5,AStep=6,ADir=7,AEnable=8,Ms1=9,Ms2=10,Ms3=11;
volatile tb::PulseState pulse;
volatile uint8_t activeStepMask=_BV(PD3);
uint8_t selectedDriver=0;

void disableHardware() {
  PORTB|=_BV(PB0); // A4988 ENABLE = HIGH
#if TB_ENABLE_WIRED
#if TB_DISABLE_LEVEL
  PORTD|=_BV(PD5);
#else
  PORTD&=uint8_t(~_BV(PD5));
#endif
#endif
}
void heartbeat() {ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {pulse.lease=tb::LeaseTicks;}}

class AvrPort:public tb::MotorPort {
 public:
  void stop()override {ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {tb::pulseStop(pulse);}}
  void rate(uint16_t pps)override {
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {pulse.rate=(pulse.fault||pulse.done)?0:(pps>tb::MaxPps?tb::MaxPps:pps);}
  }
  void finite(uint32_t count)override {
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
      pulse.phase=0;pulse.emitted=0;pulse.remaining=count;pulse.done=false;pulse.finite=count!=0;
    }
  }
  tb::Snapshot snapshot()override {
    tb::Snapshot s;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {s={pulse.remaining,pulse.emitted,pulse.rate,pulse.high,pulse.done,pulse.fault};}
    return s;
  }
  void configure(uint8_t driver,uint8_t microIndex)override {
    // Called in LOCK, after the prior pulse has finished.
    selectedDriver=driver;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {activeStepMask=driver?_BV(PD6):_BV(PD3);}
    const uint8_t mask=tb::a4988Mask(microIndex);
    digitalWrite(Ms1,(mask&1)?HIGH:LOW);digitalWrite(Ms2,(mask&2)?HIGH:LOW);digitalWrite(Ms3,(mask&4)?HIGH:LOW);
  }
  void direction(int8_t dir,bool invert)override {
    const uint8_t level=((dir>0)!=invert)?HIGH:LOW;
    digitalWrite(selectedDriver?ADir:TbDir,level);
  }
  void power(bool on)override {
    digitalWrite(AEnable,(selectedDriver==1 && on)?LOW:HIGH);
#if TB_ENABLE_WIRED
    const uint8_t disabled=TB_DISABLE_LEVEL?HIGH:LOW;
    digitalWrite(TbOff,(selectedDriver==0 && on)?(disabled==HIGH?LOW:HIGH):disabled);
#else
    (void)on; // Open ENA terminals: software cannot remove TB6600 holding current.
#endif
  }
} port;
tb::Control control(port);
hd44780_I2Cexp lcd;
bool lcdReady=false,timerReady=false;
char previousRows[2][17]={{0},{0}};
uint32_t lastSample=0,lastDisplay=0;
int rawX=512,rawY=512,filterX=512,filterY=512;
tb::Fault reportedFault=tb::NoFault;

void persist() {
  tb::seal(control.settings);
  const uint8_t *bytes=reinterpret_cast<const uint8_t *>(&control.settings);
  for(size_t i=0;i<sizeof(control.settings);++i) {
    EEPROM.update(int(i),bytes[i]);
    if(timerReady)heartbeat();
  }
  tb::Settings verify;EEPROM.get(0,verify);
  if(memcmp(&verify,&control.settings,sizeof(verify)) || !tb::validSettings(verify)) {
    control.fail(tb::StorageFault);Serial.println(F("EEPROM readback failed; LOCK"));
  }
}
void load() {
  tb::Settings saved;EEPROM.get(0,saved);
  if(tb::validSettings(saved)) {control.settings=saved;Serial.println(F("EEPROM: v2 OK"));return;}
  uint8_t legacy[30];for(uint8_t i=0;i<30;++i)legacy[i]=EEPROM.read(i);
  if(tb::migrateV1(legacy,control.settings))Serial.println(F("EEPROM: v1 migrated; DIR normal"));
  else {tb::defaults(control.settings);Serial.println(F("EEPROM: defaults loaded"));}
  persist();
}
bool calibrate(int &cx,int &cy) {
  long sx=0,sy=0;int minx=1023,miny=1023,maxx=0,maxy=0;
  for(uint8_t i=0;i<64;++i) {
    int x=analogRead(JoyX),y=analogRead(JoyY);sx+=x;sy+=y;
    if(x<minx)minx=x;if(x>maxx)maxx=x;if(y<miny)miny=y;if(y>maxy)maxy=y;
    delay(5);
  }
  cx=int(sx/64);cy=int(sy/64);
  return tb::calibrationValid(cx,cy,maxx-minx,maxy-miny);
}
bool showRows(char rows[2][17]) {
  if(!lcdReady)return false;
  // Also probe the bus when the cached screen content has not changed.
  if(lcd.setCursor(0,0)!=0 || Wire.getWireTimeoutFlag())return false;
  for(uint8_t r=0;r<2;++r) {
    uint8_t at=0;
    while(at<16) {
      if(rows[r][at]==previousRows[r][at]) {++at;continue;}
      if(lcd.setCursor(at,r)!=0)return false;
      do {
        if(lcd.write(uint8_t(rows[r][at]))!=1)return false;
        previousRows[r][at]=rows[r][at];++at;
      } while(at<16 && rows[r][at]!=previousRows[r][at]);
      if(Wire.getWireTimeoutFlag())return false;
    }
  }
  return true;
}
void diagnostic() {
  const tb::Snapshot s=port.snapshot();
  Serial.print(F("FW="));Serial.print(F(FW_VERSION));
#if defined(__LGT8FX8P__)
  Serial.print(F(" target=LGT8F328P"));
#elif defined(__LGT8FX8E__)
  Serial.print(F(" target=LGT8F328D"));
#else
  Serial.print(F(" target=ATmega328P"));
#endif
  Serial.print(F(" CPU_MHz="));Serial.print(F_CPU/1000000UL);
  Serial.print(F(" driver="));Serial.print(control.settings.selected?F("A4988"):F("TB6600"));
  Serial.print(F(" armed="));Serial.print(control.armed);
  Serial.print(F(" fault="));Serial.println(uint8_t(control.fault));
  Serial.print(F("ADC="));Serial.print(rawX);Serial.print(',');Serial.print(rawY);
  Serial.print(F(" center="));Serial.print(control.centerX);Serial.print(',');Serial.println(control.centerY);
  Serial.print(F("PPS="));Serial.print(s.rate);Serial.print(F(" left="));Serial.print(s.remaining);
  Serial.print(F(" pulses="));Serial.println(s.emitted);
  Serial.println(F("s=STOP/LOCK ?=status; no serial start command"));
}
} // namespace

ISR(TIMER1_COMPA_vect) {
  const uint8_t events=tb::pulseTick(pulse);
  if(events&tb::Falling)PORTD&=uint8_t(~activeStepMask);
  if(events&tb::Rising)PORTD|=activeStepMask;
  if(events&tb::LeaseExpired)disableHardware();
}

void testbenchSetup() {
  digitalWrite(AEnable,HIGH);pinMode(AEnable,OUTPUT);
  digitalWrite(TbOff,TB_DISABLE_LEVEL?HIGH:LOW);pinMode(TbOff,OUTPUT);
  digitalWrite(TbStep,LOW);pinMode(TbStep,OUTPUT);digitalWrite(AStep,LOW);pinMode(AStep,OUTPUT);
  digitalWrite(TbDir,LOW);pinMode(TbDir,OUTPUT);digitalWrite(ADir,LOW);pinMode(ADir,OUTPUT);
  pinMode(Ms1,OUTPUT);pinMode(Ms2,OUTPUT);pinMode(Ms3,OUTPUT);pinMode(JoySW,INPUT_PULLUP);
  Serial.begin(115200);Serial.println(F("Stepper Testbench " FW_VERSION " | leave joystick centered"));
#if defined(__LGT8F__)
  analogReadResolution(10);
  lgt_eeprom_init(1); // 1KB logical emulation, matches the LGT board's reserved flash area.
#endif
  analogReference(DEFAULT);
  Wire.begin();Wire.setClock(100000);Wire.setWireTimeout(3000,true);
  lcdReady=lcd.begin(16,2)==0;
  Wire.setWireTimeout(3000,true);
  if(lcdReady) {lcd.backlight();char intro[2][17]={"STEPPER TEST    ","Stick zentrieren"};showRows(intro);}
  load();
  int cx,cy;bool good=calibrate(cx,cy);
  rawX=filterX=cx;rawY=filterY=cy;
  control.begin(millis(),cx,cy,good);
  // Guard every direct-port pin and the ADC/I2C harness against variant remapping.
  const uint8_t pins[]={2,3,4,5,6,7,8,9,10,11,A0,A1,A4,A5};
  volatile uint8_t *const ports[]={&PORTD,&PORTD,&PORTD,&PORTD,&PORTD,&PORTD,&PORTB,&PORTB,&PORTB,&PORTB,&PORTC,&PORTC,&PORTC,&PORTC};
  const uint8_t bits[]={2,3,4,5,6,7,0,1,2,3,0,1,4,5};
  for(uint8_t i=0;i<sizeof(pins);++i) {
    if(portOutputRegister(digitalPinToPort(pins[i]))!=ports[i] || digitalPinToBitMask(pins[i])!=_BV(bits[i]))control.fail(tb::BoardFault);
  }
  if(EEPROM.length()<int(sizeof(tb::Settings)))control.fail(tb::StorageFault);
  if(!lcdReady || Wire.getWireTimeoutFlag()) {lcdReady=false;control.fail(tb::LcdFault);}
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    TCCR1A=0;TCCR1B=0;TCCR1C=0;
#if defined(__LGT8F__)
    TCKSR&=uint8_t(~0x02); // TC2XS1=0: Timer1 uses CPU clock, not the 64MHz high-speed clock.
    __asm__ __volatile__("nop\n\tnop");
#if defined(TCCR1D)
    TCCR1D=0;
#endif
#endif
    TCNT1=0;OCR1A=tb::timerCompare(F_CPU);
    TIFR1=_BV(OCF1A); // discard any pending compare event before enabling the IRQ
    TIMSK1=_BV(OCIE1A);TCCR1B=_BV(WGM12)|_BV(CS11);pulse.lease=tb::LeaseTicks;
  }
  timerReady=true;lastSample=millis();control.dirty=true;
  Serial.println(F("LOCK. Center + hold SW 1.1s, then release. Double click: menu."));
}
void testbenchLoop() {
  heartbeat();const uint32_t now=millis();
  if(tb::elapsed(now,lastSample,5)) {
    lastSample=now;rawX=analogRead(JoyX);rawY=analogRead(JoyY);
    filterX=(filterX*3+rawX)/4;filterY=(filterY*3+rawY)/4;
  }
  control.update(now,filterX,filterY,digitalRead(JoySW)==LOW);
  if(control.saveRequested) {control.saveRequested=false;persist();}
  // At most one diagnostic character per loop; serial never arms the controller.
  if(Serial.available()) {int c=Serial.read();if(c=='s'||c=='S')control.stop();else if(c=='?')diagnostic();}
  if(lcdReady && (control.dirty || tb::elapsed(now,lastDisplay,120))) {
    lastDisplay=now;control.dirty=false;char rows[2][17];tb::render(control,port.snapshot(),rows);
    if(!showRows(rows)) {lcdReady=false;control.fail(tb::LcdFault);}
  }
  if(control.fault!=reportedFault) {
    reportedFault=control.fault;Serial.print(F("LOCKED FAULT="));Serial.println(uint8_t(control.fault));
    Serial.println(F("1 LCD/I2C, 2 joystick, 3 loop lease, 4 pin map, 5 EEPROM. Fix cause; reset."));
  }
}


// ===== Stepper_Testbench_LGT8F328.ino =====
/*
  Stepper Testbench 2.1.0 — LGT8F328P/D, 16 or 32 MHz, LQFP32/48 pin harness.
  Open this file with ALL companion files in the same sketch folder.
  Library: hd44780 by Bill Perry 1.3.2; board package: lgt8fx 2.0.7.
  Pin/electrical options: Config.h. Wiring and commissioning: ../README.md.
  Timer1 is exclusive. No extra controls or electronics are needed.
*/
void setup() { testbenchSetup(); }
void loop() { testbenchLoop(); }

