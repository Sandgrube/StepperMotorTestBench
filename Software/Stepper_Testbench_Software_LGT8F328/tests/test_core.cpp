#include "Core.h"
#include "Control.h"
#include "Ui.h"
#include <assert.h>
#include <cmath>
#include <cstring>
#include <iostream>
#include <vector>
using namespace tb;
static unsigned checks=0;
#define CHECK(x) do {++checks;if(!(x)){std::cerr<<"FAIL "<<__LINE__<<": "<<#x<<"\n";std::abort();}}while(0)

struct Port:MotorPort {
  PulseState p;
  uint8_t driver=0,micro=0;
  int8_t dir=1;
  bool on=false,invalidDirectionChange=false;
  uint64_t tick=0,powerAt=0,dirAt=0,rises[2]={0,0},lastRise=0;
  unsigned badSetup=0;
  std::vector<uint16_t> finalRates;
  void stop()override {pulseStop(p);}
  void rate(uint16_t v)override {p.rate=(p.done||p.fault)?0:v;}
  void finite(uint32_t n)override {CHECK(!p.high&&!p.rate);p.phase=0;p.remaining=n;p.emitted=0;p.finite=true;p.done=false;}
  Snapshot snapshot()override {return {p.remaining,p.emitted,p.rate,p.high,p.done,p.fault};}
  void configure(uint8_t d,uint8_t m)override {CHECK(!p.high&&!p.rate);driver=d;micro=m;}
  void direction(int8_t d,bool invert)override {if(p.high||p.rate)invalidDirectionChange=true;dir=invert?-d:d;dirAt=tick;}
  void power(bool v)override {if(v&&!on)powerAt=tick;on=v;}
  void ticks(unsigned n) {
    for(unsigned i=0;i<n;++i) {
      ++tick;uint16_t before=p.rate;uint8_t e=pulseTick(p);
      if(e&Rising) {
        ++rises[driver];if(!on||tick-powerAt<50||tick-dirAt<50)++badSetup;
        if(p.done)finalRates.push_back(before);
        if(lastRise)CHECK(tick-lastRise>=2);
        lastRise=tick;
      }
      if(e&LeaseExpired)on=false;
    }
  }
};
struct Bench {
  Port port;
  Control c;
  uint32_t now;
  explicit Bench(uint32_t start=100):c(port),now(start) {}
  void begin(uint8_t driver=0,uint8_t mode=0,uint16_t deg=90) {
    c.settings.selected=driver;c.settings.p[driver].mode=mode;c.settings.p[driver].journeyDeg=deg;
    c.begin(now,512,512,true);advance(50);
  }
  void advance(unsigned ms,int x=512,int y=512,bool down=false) {
    for(unsigned i=0;i<ms;++i) {++now;port.p.lease=LeaseTicks;c.update(now,x,y,down);port.ticks(10);}
  }
  void arm() {advance(1150,512,512,true);CHECK(c.armed);CHECK(c.releaseToRun);advance(50);CHECK(c.armed&&!c.releaseToRun);}
  void click() {advance(45,512,512,true);advance(45);}
  void openMenu() {advance(400);click();click();CHECK(c.menu&&!c.armed);}
};

void testSettings() {
  Settings s;defaults(s);CHECK(validSettings(s));CHECK(sizeof(s)==32);
  CHECK(timerCompare(16000000UL)==199);CHECK(timerCompare(32000000UL)==399);
  CHECK(16000000UL/8/(timerCompare(16000000UL)+1)==TickHz);
  CHECK(32000000UL/8/(timerCompare(32000000UL)+1)==TickHz);
  CHECK(pulsesPerRev(s)==1600);s.p[0].journeyDeg=90;CHECK(journeyPulses(s)==400);seal(s);
  for(unsigned i=0;i<sizeof(s);++i) {Settings bad=s;reinterpret_cast<uint8_t *>(&bad)[i]^=0x40;CHECK(!validSettings(bad));}
  s.selected=1;for(uint8_t i=0;i<5;++i) {s.p[1].microIndex=i;CHECK(a4988Mask(i)==(i==4?7:i));}
  s.p[1].microIndex=5;seal(s);CHECK(!validSettings(s));
  defaults(s);s.p[0].maxRpm=7;seal(s);CHECK(!validSettings(s));
  defaults(s);uint8_t old[30]={0};memcpy(old,&s.magic,4);old[4]=1;old[5]=1;
  memcpy(old+6,&s.p[0],11);memcpy(old+17,&s.p[1],11);
  uint16_t crc=crc16(old,28);memcpy(old+28,&crc,2);Settings migrated;
  CHECK(migrateV1(old,migrated));CHECK(migrated.selected==1&&validSettings(migrated));
  CHECK(migrated.p[0].invert==0&&migrated.p[1].invert==0);
  old[12]^=1;CHECK(!migrateV1(old,migrated));
  CHECK(crc16("123456789",9)==0x29b1);
  CHECK(cycle(RpmOptions,12,3,-1)==240);CHECK(cycle(RpmOptions,12,240,1)==3);
  std::cout<<"settings/CRC/migration: PASS\n";
}
void testAxes() {
  Settings s;defaults(s);uint8_t pc=99;
  CHECK(speedFromY(512,512,s,pc)==0&&pc==0);
  for(int center=350;center<=674;center+=27) {
    CHECK(speedFromY(0,center,s,pc)==400&&pc==100);
    CHECK(speedFromY(1023,center,s,pc)==400&&pc==100);
    for(int raw=0;raw<1024;++raw) {uint16_t v=speedFromY(raw,center,s,pc);CHECK(v<=MaxPps&&pc<=100);}
  }
  s.p[0].fullSteps=400;s.p[0].microIndex=5;s.p[0].maxRpm=240;s.p[0].journeyDeg=1440;
  CHECK(speedFromY(0,512,s,pc)==4000);CHECK(journeyPulses(s)==51200);
  CHECK(calibrationValid(512,500,39,40));CHECK(!calibrationValid(100,500,0,0));CHECK(!calibrationValid(500,500,41,0));
  CHECK(neutral(512,512,512,512));CHECK(!neutral(800,512,512,512));
  std::cout<<"axes/calibration/rate and distance limits: PASS\n";
}
void testPulses() {
  for(uint16_t rate=1;rate<=MaxPps;++rate) {
    PulseState p;p.rate=rate;unsigned pulses=0,last=0;
    for(unsigned t=1;t<=TickHz;++t) {
      p.lease=LeaseTicks;uint8_t e=pulseTick(p);
      if(e&Rising) {if(last)CHECK(t-last>=2);last=t;++pulses;}
      CHECK((e&(Rising|Falling))!=(Rising|Falling));
    }
    CHECK(pulses==rate);
  }
  for(uint32_t n: {1UL,2UL,400UL,51200UL}) {
    PulseState p;p.rate=4000;p.finite=true;p.remaining=n;
    for(uint32_t t=0;t<n*3+10;++t) {p.lease=LeaseTicks;pulseTick(p);}
    CHECK(p.emitted==n&&p.done&&!p.high&&p.remaining==0);
    p.rate=4000;for(int i=0;i<100;++i){p.lease=LeaseTicks;pulseTick(p);}CHECK(p.emitted==n);
  }
  PulseState p;p.rate=4000;while(!p.high){p.lease=LeaseTicks;pulseTick(p);}
  uint32_t before=p.emitted;pulseStop(p);CHECK(p.high);
  CHECK(pulseTick(p)&Falling);CHECK(!p.high&&p.emitted==before);
  p.rate=4000;p.lease=LeaseTicks;for(int i=0;i<1002;++i)pulseTick(p);
  CHECK(p.fault&&!p.rate&&!p.high);before=p.emitted;p.lease=LeaseTicks;p.rate=4000;
  for(int i=0;i<100;++i)pulseTick(p);
  CHECK(p.emitted==before);
  std::cout<<"all 4000 rates / finite blocks / pulse completion / lease: PASS\n";
}
void testButtonAndWrap() {
  Bench b(0xfffffd00UL);b.begin();b.arm();CHECK(b.c.armed); // hold crosses millis rollover
  b.advance(1000,1023,1023);CHECK(b.port.rises[0]>0);
  b.click();CHECK(!b.c.armed&&!b.port.p.rate&&!b.port.on);
  Bench bad;bad.begin();bad.advance(500,512,512,true);bad.advance(100,900,512,true);bad.advance(1500,512,512,true);
  CHECK(!bad.c.armed);bad.advance(50);bad.arm();
  Bench held;held.begin();held.advance(1150,512,512,true);held.advance(500,1023,1023,true);
  CHECK(held.c.armed&&held.port.rises[0]==0);held.advance(50);held.advance(1000,1023,1023);CHECK(held.port.rises[0]>0);
  Repeat r;CHECK(r.update(0xffffff00UL,1));CHECK(!r.update(0xffffff80UL,1));CHECK(r.update(0x100UL,1));
  std::cout<<"button gestures / continuous neutral / release gate / millis wrap: PASS\n";
}
void testControl() {
  Bench b;b.begin(1);b.advance(1000,1023,1023);CHECK(b.port.rises[0]+b.port.rises[1]==0);
  b.arm();b.advance(1200,1023,1023);CHECK(b.port.rises[1]>0&&b.port.rises[0]==0);CHECK(b.port.p.rate==400);
  b.advance(1000,0,1023);CHECK(b.port.dir==-1&&!b.port.invalidDirectionChange);CHECK(b.port.badSetup==0);
  b.advance(1000);CHECK(b.port.p.rate==0&&!b.port.on);
  b.c.settings.p[1].hold=1;b.advance(100);CHECK(b.port.on);b.click();CHECK(!b.port.on&&!b.c.armed);
  b.openMenu();b.advance(50,1023,512);CHECK(b.c.settings.selected==0);b.advance(50);b.click();
  CHECK(!b.c.menu&&!b.c.armed&&b.c.saveRequested&&b.port.driver==0);
  b.advance(1000,1023,1023);CHECK(!b.port.p.rate);
  Bench f;f.begin(1);f.arm();f.advance(500,1023,1023);f.port.ticks(1005);
  CHECK(f.port.p.fault&&!f.port.on);f.advance(1);CHECK(f.c.fault==LoopFault&&!f.c.armed);
  f.advance(2000,512,512,true);CHECK(!f.c.armed);
  Bench lcd;lcd.begin();lcd.arm();lcd.advance(300,1023,1023);lcd.c.fail(LcdFault);lcd.advance(1000,1023,1023);CHECK(!lcd.c.armed&&!lcd.port.on&&!lcd.port.p.rate);
  std::cout<<"continuous / driver selection / reverse / hold / menu / fault latches: PASS\n";
}
void testJourney() {
  Bench b;b.begin(1,1,90);b.arm();b.advance(300,1023,1023);CHECK(b.c.journeyRunning);
  b.advance(200);b.advance(5000,1023,1023);CHECK(!b.c.journeyRunning);
  CHECK(b.port.p.emitted==400&&b.port.rises[1]==400);CHECK(b.port.badSetup==0);
  b.advance(5000,0,1023);CHECK(b.port.rises[1]==400); // no reversal/repeat until post-completion center
  b.advance(50);b.advance(5000,0,1023);CHECK(b.port.rises[1]==800);
  Bench stop;stop.begin(1,1);stop.arm();stop.advance(300,1023,1023);stop.click();
  uint64_t n=stop.port.rises[1];CHECK(n>0&&n<400);stop.advance(5000,1023,1023);CHECK(stop.port.rises[1]==n);
  for(uint8_t driver=0;driver<2;++driver) for(uint16_t deg:DegreeOptions) {
    Bench test;test.begin(driver,1,deg);test.arm();test.advance(20000,1023,1023);
    CHECK(test.port.p.emitted==journeyPulses(test.c.settings));CHECK(!test.c.journeyRunning);CHECK(test.port.badSetup==0);
  }
  Bench tiny;tiny.c.settings.p[0].fullSteps=48;tiny.c.settings.p[0].microIndex=0;tiny.c.settings.p[0].accelRpmPerSec=10;
  tiny.begin(0,1,15);tiny.arm();tiny.advance(5000,1023,1023);CHECK(tiny.port.p.emitted==2&&!tiny.c.journeyRunning);
  Bench largest;largest.c.settings.p[0].fullSteps=400;largest.c.settings.p[0].microIndex=5;largest.c.settings.p[0].maxRpm=240;
  largest.begin(0,1,1440);largest.arm();largest.advance(20000,1023,1023);CHECK(largest.port.p.emitted==51200&&!largest.c.journeyRunning);
  std::cout<<"journey exact counts / no queued repeat / cancel / all angle presets: PASS\n";
}
void testStartupMatrix() {
  for(uint8_t driver=0;driver<2;++driver)for(uint16_t full:FullStepOptions)for(uint8_t micro=0;micro<(driver?5:6);++micro) {
    Bench b;b.c.settings.p[driver].fullSteps=full;b.c.settings.p[driver].microIndex=micro;
    b.c.settings.p[driver].maxRpm=3;b.c.settings.p[driver].accelRpmPerSec=10;
    b.begin(driver);b.arm();b.advance(2000,1023,1023);
    CHECK(b.port.rises[driver]>0&&b.port.badSetup==0);
    b.advance(3000);CHECK(!b.port.p.rate&&!b.port.on&&!b.port.invalidDirectionChange);
  }
  std::cout<<"low-speed startup/stop matrix: both drivers, all full-step and microstep presets: PASS\n";
}
void testUi() {
  Bench b;b.begin();char rows[2][17];
  for(uint8_t driver=0;driver<2;++driver)for(uint8_t page=0;page<MenuCount;++page) {
    b.c.menu=true;b.c.page=page;b.c.settings.selected=driver;render(b.c,b.port.snapshot(),rows);
    CHECK(strlen(rows[0])==16&&strlen(rows[1])==16);
  }
  for(uint8_t f=1;f<=5;++f){b.c.fault=Fault(f);render(b.c,b.port.snapshot(),rows);CHECK(strlen(rows[0])==16&&strlen(rows[1])==16);}
  std::cout<<"16x2 UI buffers / all menus and faults: PASS\n";
}
int main() {
  testSettings();testAxes();testPulses();testButtonAndWrap();testControl();testJourney();testStartupMatrix();testUi();
  std::cout<<"PASS: "<<checks<<" assertions (includes scheduler sweeps).\n";
}

