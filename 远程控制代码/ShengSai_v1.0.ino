#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>  // I2C通信所需的库
#include "PS2X_lib.h"  // PS2控制器库

#define FrontLeftWheelZ 22
#define FrontLeftWheelF 23
#define FrontRightWheelZ 24
#define FrontRightWheelF 25
#define BackLeftWheelZ 26
#define BackLeftWheelF 27
#define BackRightWheelZ 28
#define BackRightWheelF 29
#define EnFrontLeft 2
#define EnFrontRight 3
#define EnBackLeft 4
#define EnBackRight 5

PS2X ps2x; 

Servo servo_1;
int error = 0; 
byte type = 0;
byte vibrate = 0;

/******************************************************************/
//车轮控制函数
void Forward(int speed,int time) 
{
    digitalWrite(FrontLeftWheelZ,0);
    digitalWrite(FrontLeftWheelF,1);
    digitalWrite(FrontRightWheelZ,1);
    digitalWrite(FrontRightWheelF,0);
    digitalWrite(BackLeftWheelZ,0);
    digitalWrite(BackLeftWheelF,1);
    digitalWrite(BackRightWheelZ,1);
    digitalWrite(BackRightWheelF,0);
    analogWrite(EnFrontLeft,speed);
    analogWrite(EnFrontRight,speed);
    analogWrite(EnBackLeft,speed);
    analogWrite(EnBackRight,speed);
    delay(time);
}

void Backward(int speed,int time) 
{
    digitalWrite(FrontLeftWheelZ,1);
    digitalWrite(FrontLeftWheelF,0);
    digitalWrite(FrontRightWheelZ,0);
    digitalWrite(FrontRightWheelF,1);
    digitalWrite(BackLeftWheelZ,1);
    digitalWrite(BackLeftWheelF,0);
    digitalWrite(BackRightWheelZ,0);
    digitalWrite(BackRightWheelF,1);
    analogWrite(EnFrontLeft,speed);
    analogWrite(EnFrontRight,speed);
    analogWrite(EnBackLeft,speed);
    analogWrite(EnBackRight,speed);
    delay(time);
}

void Left(int speed,int time) 
{
    digitalWrite(FrontLeftWheelZ,1);
    digitalWrite(FrontLeftWheelF,0);
    digitalWrite(FrontRightWheelZ,1);
    digitalWrite(FrontRightWheelF,0);
    digitalWrite(BackLeftWheelZ,0);
    digitalWrite(BackLeftWheelF,1);
    digitalWrite(BackRightWheelZ,0);
    digitalWrite(BackRightWheelF,1);
    analogWrite(EnFrontLeft,speed);
    analogWrite(EnFrontRight,speed);
    analogWrite(EnBackLeft,speed);
    analogWrite(EnBackRight,speed);
    delay(time);
}

void Right(int speed,int time) 
{
    digitalWrite(FrontLeftWheelZ,0);
    digitalWrite(FrontLeftWheelF,1);
    digitalWrite(FrontRightWheelZ,0);
    digitalWrite(FrontRightWheelF,1);
    digitalWrite(BackLeftWheelZ,1);
    digitalWrite(BackLeftWheelF,0);
    digitalWrite(BackRightWheelZ,1);
    digitalWrite(BackRightWheelF,0);
    analogWrite(EnFrontLeft,speed);
    analogWrite(EnFrontRight,speed);
    analogWrite(EnBackLeft,speed);
    analogWrite(EnBackRight,speed);
    delay(time);
}

void TurnLeft(int speed,int time) 
{
    digitalWrite(FrontLeftWheelZ,1);
    digitalWrite(FrontLeftWheelF,0);
    digitalWrite(FrontRightWheelZ,1);
    digitalWrite(FrontRightWheelF,0);
    digitalWrite(BackLeftWheelZ,1);
    digitalWrite(BackLeftWheelF,0);
    digitalWrite(BackRightWheelZ,1);
    digitalWrite(BackRightWheelF,0);
    analogWrite(EnFrontLeft,speed);
    analogWrite(EnFrontRight,speed);
    analogWrite(EnBackLeft,speed);
    analogWrite(EnBackRight,speed);
    delay(time);
}

void TurnRight(int speed,int time) 
{
    digitalWrite(FrontLeftWheelZ,0);
    digitalWrite(FrontLeftWheelF,1);
    digitalWrite(FrontRightWheelZ,0);
    digitalWrite(FrontRightWheelF,1);
    digitalWrite(BackLeftWheelZ,0);
    digitalWrite(BackLeftWheelF,1);
    digitalWrite(BackRightWheelZ,0);
    digitalWrite(BackRightWheelF,1);
    analogWrite(EnFrontLeft,speed);
    analogWrite(EnFrontRight,speed);
    analogWrite(EnBackLeft,speed);
    analogWrite(EnBackRight,speed);
    delay(time);
}

void Stop(int time) 
{
   digitalWrite(FrontLeftWheelZ,0);
    digitalWrite(FrontLeftWheelF,0);
    digitalWrite(FrontRightWheelZ,0);
    digitalWrite(FrontRightWheelF,0);
    digitalWrite(BackLeftWheelZ,0);
    digitalWrite(BackLeftWheelF,0);
    digitalWrite(BackRightWheelZ,0);
    digitalWrite(BackRightWheelF,0);
    analogWrite(EnFrontLeft,0);
    analogWrite(EnFrontRight,0);
    analogWrite(EnBackLeft,0);
    analogWrite(EnBackRight,0);
    delay(time);
}
/******************************************************************/

/******************************************************************/
//夹爪控制函数
void Close()
{
    servo_1.write(33);
}

void Open()
{
    servo_1.write(3);
}
/******************************************************************/

/******************************************************************/
//PS2通信函数
void MyPSFunc(int time)
{
    if(error == 1) 
  return; 
  
 if(type == 2){ 
   
   ps2x.read_gamepad();          //read controller 
   
   if(ps2x.ButtonPressed(GREEN_FRET))
     Serial.println("Green Fret Pressed");
   if(ps2x.ButtonPressed(RED_FRET))
     Serial.println("Red Fret Pressed");
   if(ps2x.ButtonPressed(YELLOW_FRET))
     Serial.println("Yellow Fret Pressed");
   if(ps2x.ButtonPressed(BLUE_FRET))
     Serial.println("Blue Fret Pressed");
   if(ps2x.ButtonPressed(ORANGE_FRET))
     Serial.println("Orange Fret Pressed");
     

    if(ps2x.ButtonPressed(STAR_POWER))
     Serial.println("Star Power Command");
    
    if(ps2x.Button(UP_STRUM))          //will be TRUE as long as button is pressed
     Serial.println("Up Strum");
    if(ps2x.Button(DOWN_STRUM))
     Serial.println("DOWN Strum");
  
 
    if(ps2x.Button(PSB_START))                   //will be TRUE as long as button is pressed
         Serial.println("Start is being held");
    if(ps2x.Button(PSB_SELECT))
         Serial.println("Select is being held");

    
    if(ps2x.Button(ORANGE_FRET)) // print stick value IF TRUE
    {
        Serial.print("Wammy Bar Position:");
        Serial.println(ps2x.Analog(WHAMMY_BAR), DEC); 
    } 
 }

 else { //DualShock Controller
  
    ps2x.read_gamepad(false, vibrate);          //read controller and set large motor to spin at 'vibrate' speed
    
    if(ps2x.Button(PSB_START))                   //will be TRUE as long as button is pressed
         Serial.println("Start is being held");
    if(ps2x.Button(PSB_SELECT))
         Serial.println("Select is being held");
         
         
     if(ps2x.Button(PSB_PAD_UP)) {         //will be TRUE as long as button is pressed
       Serial.print("Up held this hard: ");
       Serial.println(ps2x.Analog(PSAB_PAD_UP), DEC);
      }
      if(ps2x.Button(PSB_PAD_RIGHT)){
       Serial.print("Right held this hard: ");
        Serial.println(ps2x.Analog(PSAB_PAD_RIGHT), DEC);
      }
      if(ps2x.Button(PSB_PAD_LEFT)){
       Serial.print("LEFT held this hard: ");
        Serial.println(ps2x.Analog(PSAB_PAD_LEFT), DEC);
      }
      if(ps2x.Button(PSB_PAD_DOWN)){
       Serial.print("DOWN held this hard: ");
     Serial.println(ps2x.Analog(PSAB_PAD_DOWN), DEC);
      }   
  
    
      vibrate = ps2x.Analog(PSAB_BLUE);        //this will set the large motor vibrate speed based on 
                                              //how hard you press the blue (X) button    
    
    if (ps2x.NewButtonState())               //will be TRUE if any button changes state (on to off, or off to on)
    {   
        if(ps2x.Button(PSB_L3))
         Serial.println("L3 pressed");
        if(ps2x.Button(PSB_R3))
         Serial.println("R3 pressed");
        if(ps2x.Button(PSB_L2))
        {
            Serial.println("L2 pressed");
            // Serial.println(ps2x.Analog(PSB_L2), DEC);
        }
        if(ps2x.Button(PSB_R2))
         Serial.println("R2 pressed");
        if(ps2x.Button(PSB_GREEN))
         Serial.println("Triangle pressed");
         
    }   
         
    
    if(ps2x.ButtonPressed(PSB_RED))             //will be TRUE if button was JUST pressed
    {
        Serial.println("Circle just pressed");
        Close();
    }       
         
    if(ps2x.ButtonReleased(PSB_PINK))             //will be TRUE if button was JUST released
    {
        Serial.println("Square just released");
        Open();
    }       
    
    if(ps2x.NewButtonState(PSB_BLUE))            //will be TRUE if button was JUST pressed OR released
         Serial.println("X just changed");    
    
    
    if(ps2x.Button(PSB_L1) || ps2x.Button(PSB_R1)) // print stick values if either is TRUE
    {
        Serial.print("Stick Values:");
        Serial.print(ps2x.Analog(PSS_LY), DEC); //Left stick, Y axis. Other options: LX, RY, RX  
        Serial.print(",");
        Serial.print(ps2x.Analog(PSS_LX), DEC); 
        Serial.print(",");
        Serial.print(ps2x.Analog(PSS_RY), DEC); 
        Serial.print(",");
        Serial.println(ps2x.Analog(PSS_RX), DEC); 
    } 

 }

 delay(time);
}
/******************************************************************/

void setup() 
{
  // 初始化电机控制引脚为输出模式
  pinMode(FrontLeftWheelZ, OUTPUT);
  pinMode(FrontLeftWheelF, OUTPUT);
  pinMode(FrontRightWheelZ, OUTPUT);
  pinMode(FrontRightWheelF, OUTPUT);
  pinMode(BackLeftWheelZ, OUTPUT);
  pinMode(BackLeftWheelF, OUTPUT);
  pinMode(BackRightWheelZ, OUTPUT);
  pinMode(BackRightWheelF, OUTPUT);

//手柄通信
  error = ps2x.config_gamepad(17,15,16,14, true, true);   //GamePad(clock, command, attention, data, Pressures?, Rumble?) 
 
 if(error == 0){
   Serial.println("Found Controller, configured successful");
 }
   
  else if(error == 1)
   Serial.println("No controller found, check wiring, see readme.txt to enable debug. visit www.billporter.info for troubleshooting tips");
   
  else if(error == 2)
   Serial.println("Controller found but not accepting commands. see readme.txt to enable debug. Visit www.billporter.info for troubleshooting tips");
   
  else if(error == 3)
   Serial.println("Controller refusing to enter Pressures mode, may not support it. ");
      
   type = ps2x.readType(); 
     switch(type) {
       case 0:
        Serial.println("Unknown Controller type");
       break;
       case 1:
        Serial.println("DualShock Controller Found");
       break;
       case 2:
         Serial.println("GuitarHero Controller Found");
       break;
     }

  servo_1.attach(8);
  servo_1.write(3);
  
  Serial.begin(115200);

  // 初始时停止
  Stop(0);
}

void loop() 
{
    MyPSFunc(20);
}