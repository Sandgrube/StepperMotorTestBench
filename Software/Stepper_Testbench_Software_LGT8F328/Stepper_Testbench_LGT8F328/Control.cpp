#include "Control.h"
#include "Config.h"
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

