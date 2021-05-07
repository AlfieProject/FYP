#include <VarSpeedServo.h>

String Read;
String tempString;
String split;
int ID;
int Angle;
int marker1;
int marker2;

VarSpeedServo servo1;
VarSpeedServo servo2;
VarSpeedServo servo3;
VarSpeedServo servo4;
VarSpeedServo servo5;

int get_values(String data, int index)
{
  int i;
  marker2 = 0;
  for (i = 0; i <= data.length(); i++) {
    if (data.charAt(i) == ':') {
      if (index == 0) {
        split = data.substring(marker2-1, (i)).toInt();
      }
      else {
        split = data.substring(marker2 + 1, data.length()).toInt();
      }
    }
    marker2 = i + 1;
  }
  return split;
}

void setup() 
{ 
  Serial.begin(9600);
  servo1.attach(11);
  servo1.write(0, 10, false);
  
  servo2.attach(10);
  servo2.write(50, 10, false);
  
  servo3.attach(9, 800, 2100);
  servo3.write(30, 10, false);
  
  servo4.attach(6);
  servo4.write(30, 10, false);
  
  servo5.attach(5);
  servo5.write(90, 10, false);
}

void loop() 
{
  if(Serial.available() > 0) {
    Read = Serial.readStringUntil('\n');
    ID = get_values(Read, ':', 0);
    Angle = get_values(Read, ':', 1);
    
    int i;

    marker = 0;
    for (i = 0; i <= Read.length(); i++) {
      if (Read.charAt(i) == '#') {
        tempString = Read.substring(marker1, (i));
        ID = getValue(tempString, 0);
        Angle = getValue(tempString, 1);
        switch (ID) {
          case 1:
            if ((Angle > -1) and (Angle < 181)) {
              servo1.write(Angle, 50, false);
              break;
            }
          case 2:
            if ((Angle > -1) and (Angle < 121)) {
              servo2.write(Angle, 10, false);
              break;
            }
          case 3:
            if ((Angle > -1) and (Angle < 181)) {
              servo3.write(Angle, 10, false);
              break;
            }
          case 4:
            if ((Angle > -1) and (Angle < 181)) {
              servo4.write(Angle, 10, false);
              break;
            }
          case 5:
            if ((Angle > -1) and (Angle < 101)) {
              servo5.write(Angle, 10, false);
              break;
            }
        }
        marker1 = i + 1;
      }
    }
  }
}
