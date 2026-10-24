#include "App.h"
#include "Config.h"
#include "Control.h"
#include "Ui.h"
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

