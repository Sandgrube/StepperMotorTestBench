#include "Ui.h"
#include "Config.h"
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

