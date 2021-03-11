#include<Wire.h>
#include <MechaQMC5883.h>
MechaQMC5883 qmc;
const int MPU=0x68; 
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
int16_t AcXCal,AcYCal,AcZCal,TmpCal,GyXCal,GyYCal,GyZCal;
float smoothedValAcX,smoothedValAcY,smoothedValAcZ,smoothedValGyX=0.0,smoothedValGyY=0.0,smoothedValGyZ=0.0;
float xac,yac,zac,xgy,ygy,zgy;
int minVal=265,maxVal=402;
int i = 0;
int callibration=8,SHOT=9;
int azimuth;

//New (better) control program for MPU6050
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  #include "Wire.h"
#endif
MPU6050 mpu;
#define OUTPUT_READABLE_QUATERNION
#define INTERRUPT_PIN 2
#define LED_PIN 13
bool blinkState = false;
// control variables
bool dmpReady = false;
uint8_t mpuIntStatus;
uint8_t devStatus;
uint16_t packetSize;
uint16_t fifoCount;
uint8_t fifoBuffer[64];
// motion and orientation variables
Quaternion q;
VectorInt16 aa;
VectorInt16 aaReal;
VectorInt16 aaWorld;
VectorFloat gravity;
float euler[3];
float ypr[3];

// interrupt detection
volatile bool mpuInterrupt = false;
void dmpDataReady() {
  mpuInterrupt = true;
}

void setup(){
  pinMode(SHOT, INPUT);
  pinMode(callibration, INPUT);
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);
  Serial.begin(9600);
  pinMode(2, INPUT);
  i2csetup();
  Serial.println("Done Callibrating");
}

void loop(){
  i = 0;
  getPosition();
  //SHOT
  if (digitalRead(SHOT) == HIGH){
    shot();
  }
  delay(20);
}

void i2csetup(){
  // join i2c bus
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    Wire.begin();
    Wire.setClock(400000);
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
    Fastwire::setup(400,true);
  #endif
  
  // initialize device(s)
  Serial.println(F("Initializing I2C devices..."));
  mpu.initialize();
  pinMode(INTERRUPT_PIN, INPUT);
  // verify connection(s)
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));
  
  // start mpu when ready
  Serial.println(F("\nWaiting for callibration pin to go high: "));
  while (digitalRead(callibration) == LOW){
  }
  // load & config DMP
  Serial.println(F("Initalizing DMP..."));
  devStatus = mpu.dmpInitialize();
  // gyro offsets:
  mpu.setXGyroOffset(220);
  mpu.setYGyroOffset(76);
  mpu.setZGyroOffset(-85);
  mpu.setZAccelOffset(1788);
  
  // continue if it worked
  if (devStatus == 0) {
    mpu.CalibrateAccel(6);
    mpu.CalibrateGyro(6);
    mpu.PrintActiveOffsets();
    Serial.println(F("Enabling DMP..."));
    mpu.setDMPEnabled(true);
    
    // enable interrupt detection
    Serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
    Serial.print(digitalPinToInterrupt(INTERRUPT_PIN));
    Serial.println(F(")..."));
    attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();
    // state ready
    Serial.println(F("DMP ready, waiting for first interrupt..."));
    dmpReady = true;
    packetSize = mpu.dmpGetFIFOPacketSize();
  }
  
  else {
    // 1 = initial memory load failed
    // 2 = DMP configuration updates failed
    // (if it's going to break, usually the code will be 1)
    Serial.print(F("DMP Initialization failed (code "));
    Serial.print(devStatus);
    Serial.println(F(")"));
  }
  pinMode(LED_PIN, OUTPUT);
}

void shot(){
  int laserPin=12;
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, HIGH);
  delay(500);
  Serial.println("Execute Confirmation");
  while(digitalRead(SHOT) == LOW){
  }
  digitalWrite(laserPin, LOW);
  delay(7000);
  Serial.println("Position Data:");
  for (int i = 0; i <= 400; i++) {
    getPosition();
    Serial.print("Xac:");Serial.print(xac);Serial.print(",Yac:");
    Serial.print(yac);Serial.print(",Zac:");Serial.println(azimuth);
    delay(5);
  }
  Serial.println("Distance Data:");
  float distance = 0.0;
  for (int i = 0; i <= 30; i ++) {
    distance = ultrasonicPing();
    Serial.println(distance);
    delay(40);
  }
}

void getPosition(){
  int x, y, z;
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  float filterVal = .985 ;
  if (filterVal > 1){
    filterVal = .99;
  }
  else if (filterVal <= 0){
    filterVal = 0;
  }
  qmc.read(&x, &y, &z,&azimuth);
  //Accelerometer to angle
  AcX = AcX - AcXCal;
  AcY = AcY - AcYCal;
  AcZ = AcZ - AcZCal;
  smoothedValAcX = lowPassFilterAcX(AcX, filterVal, smoothedValAcX);
  smoothedValAcY = lowPassFilterAcY(AcY, filterVal, smoothedValAcY);
  smoothedValAcZ = lowPassFilterAcZ(AcZ, filterVal, smoothedValAcZ);
  int xAng = map(AcX,minVal,maxVal,-90,90);
  int yAng = map(AcY,minVal,maxVal,-90,90);
  int zAng = map(AcZ,minVal,maxVal,-90,90);
  xac= RAD_TO_DEG * (atan2(-yAng, -zAng)+PI);
  yac= RAD_TO_DEG * (atan2(-xAng, -zAng)+PI);
  zac= RAD_TO_DEG * (atan2(-yAng, -xAng)+PI);
}

float ultrasonicPing(){
  long duration, inches;
  pinMode(10, OUTPUT);
  digitalWrite(10, LOW);
  delayMicroseconds(2);
  digitalWrite(10, HIGH);
  delayMicroseconds(10);
  digitalWrite(10, LOW);
  pinMode(11, INPUT);
  duration = pulseIn(11, HIGH);
  inches = microsecondsToInches(duration);
  return inches;
}
long microsecondsToInches(long microseconds){
  return microseconds/74/2;
}
int lowPassFilterAcX(int in, float filterVal, float smoothedValAcX){
  smoothedValAcX = (in*(1-filterVal)) + (smoothedValAcX*filterVal);
  return smoothedValAcX;
}
int lowPassFilterAcY(int in, float filterVal, float smoothedValAcY){
  smoothedValAcY = (in*(1-filterVal)) + (smoothedValAcY*filterVal);
  return smoothedValAcY;
}
int lowPassFilterAcZ(int in, float filterVal, float smoothedValAcZ){
  smoothedValAcZ = (in*(1-filterVal)) + (smoothedValAcZ*filterVal);
  return smoothedValAcZ;
}
