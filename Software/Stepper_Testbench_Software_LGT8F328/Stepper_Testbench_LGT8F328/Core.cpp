#include "Core.h"
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

