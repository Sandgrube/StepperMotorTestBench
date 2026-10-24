#pragma once
#include "Core.h"

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

