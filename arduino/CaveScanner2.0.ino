#include<Wire.h>
#include <MechaQMC5883.h>
MechaQMC5883 qmc;
const int MPU=0x68; 
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
  String command;
  command = serial_input();
  if (command == "position") {
    getPosition();
  }
  else if (command == "position_continous") {
    while (1==1){
      command = serial_input();
      if (command == "stop"){
        break;
      }
      getPosition();
    }
  }
  else if (command == "ping") {
    float distance = ultrasonicPing();
    Serial.println(distance);
  }
  else if (command == "ping_continous") {
    while (1==1){
      command = serial_input();
      if (command == "stop"){
        break;
      }
      float distance = ultrasonicPing();
      Serial.println(distance);
    }
  }
  else if (command == "position_ping"){
    while (1==1){
      command = serial_input();
      if (command == "stop"){
        break;
      }
      getPosition();
      float distance = ultrasonicPing();
      Serial.println(distance);
    }
  }
  else if (command == "laser_on"){
    laser_on();
  }
  else if (command == "laser_off"){
    laser_off();
  }
  //SHOT
  if (digitalRead(SHOT) == HIGH){
    shot();
  }
  delay(20);
}

String serial_input(){
  String input;
  if (Serial.available() > 0) {
    input = Serial.readString();
    input.trim();
    Serial.print("Command received: ");
    Serial.println(input);
  }
  return input;
}

void callibration_continue(){
  boolean move_on = false;
  while (move_on == false){
    if (Serial.available() > 0) {
      String cont = Serial.readString();
      Serial.println("Continuing callibration as requested over SERIAL.");
      move_on == true;
      break;
    }
    else if (digitalRead(callibration) == HIGH) {
      Serial.println("Continuing callibration as requested by GPIO");
      move_on == true;
      break;
    }
  }
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
  callibration_continue();
  
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

long microsecondsToInches(long microseconds){
  return microseconds/74/2;
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

int laserPin = 12;
void laser_on(){
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, HIGH);
}
void laser_off(){
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, LOW);
}

void shot(){
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, HIGH);
  delay(500);
  Serial.println("Execute Confirmation");
  while(digitalRead(SHOT) == LOW){
  }
  digitalWrite(laserPin, LOW);
  delay(7000);
  Serial.println("Position Data:");
  for (int i = 0; i <= 15; i++) {
    getPosition();
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
   if (!dmpReady) return;
    // read a packet from FIFO
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // Get the Latest packet 
        #ifdef OUTPUT_READABLE_QUATERNION
            // display quaternion values in easy matrix form: w x y z
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            Serial.print("quat\t");
            Serial.print(q.w);
            Serial.print("\t");
            Serial.print(q.x);
            Serial.print("\t");
            Serial.print(q.y);
            Serial.print("\t");
            Serial.println(q.z);
        #endif
    }
}
