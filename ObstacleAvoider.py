#!/usr/bin/python
from __future__ import print_function
import time, signal, sys
from pololu_drv8835_rpi import motors, MAX_SPEED 
from Adafruit_ADS1x15 import ADS1x15

def signal_handler(signal, frame):
        motors.setSpeeds(0, 0) 
        print ('You pressed Ctrl+C!')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
#print 'Press Ctrl+C to exit'


OBSTACLE_FAR   =  30   # 30cm
OBSTACLE_NEAR  =  20   # 20cm
OBSTACLE_CLOSE =  10   # 10cm

class ADS1015(object):
  ADS1015 = 0x00  # 12-bit ADC
  ADS1115 = 0x01	# 16-bit ADC

  # Select the gain
  # gain = 6144  # +/- 6.144V
  gain = 4096  # +/- 4.096V
  # gain = 2048  # +/- 2.048V
  # gain = 1024  # +/- 1.024V
  # gain = 512   # +/- 0.512V
  # gain = 256   # +/- 0.256V

  # Select the sample rate
  # sps = 8    # 8 samples per second
  # sps = 16   # 16 samples per second
  # sps = 32   # 32 samples per second
  # sps = 64   # 64 samples per second
  # sps = 128  # 128 samples per second
  sps = 250  # 250 samples per second
  # sps = 475  # 475 samples per second
  # sps = 860  # 860 samples per second
  adc = ADS1x15(ic=ADS1015)

  def __init__(self):
    self.gain = 2048  # +/- 2.048V
    self.sps = 250  # 250 samples per second
    # Initialise the ADC using the default mode (use default I2C address)
    # Set this to ADS1015 or ADS1115 depending on the ADC you are using!

  def read(self, port):
    value = self.adc.readADCSingleEnded(port, self.gain, self.sps)
    return value

class Motor(object):
    speedL = 0
    speedR = 0
    actSpeedL = 0
    actSpeedR = 0
    SPEED_STEP = 10

    def __init__(self):
      self.speedL = 0
      self.speedR = 0
      self.actSpeedL = 0
      self.actSpeedR = 0
 
    def setSpeed(self, sr, sl):
      self.speedL = sr
      self.speedR = sl
      print ("speed", self.speedR, self.speedL)

    def updateMotors(self):
      if self.speedL == 0:
        self.actSpeedL = 0
      elif self.actSpeedL < self.speedL:
        self.actSpeedL += self.SPEED_STEP
      elif self.actSpeedL > self.speedL:
        self.actSpeedL -= self.SPEED_STEP
      if self.speedR == 0:
        self.actSpeedR = 0
      elif self.actSpeedR < self.speedR:
        self.actSpeedR += self.SPEED_STEP
      elif self.actSpeedR > self.speedR:
        self.actSpeedR -= self.SPEED_STEP
      print ("motor lt, rt", self.actSpeedR, self.actSpeedL)
      motors.setSpeeds(self.actSpeedR, self.actSpeedL)
      time.sleep(0.100) 

if __name__ == "__main__":
    print ('roboPi obstacle avoider')
    ads1015 = ADS1015()
    motor = Motor()
    motors.setSpeeds(0, 0)  


    while 1:
      try: 
        # Read channel 3 in single-ended mode using the settings above
        value = ads1015.read(0)
        distance = 14 / (value/1000 - 0.1)
        print ("value: {0:.0f} mV distance: {1:.0f} cm".format(value, distance))

        if distance > OBSTACLE_CLOSE:
            motor.setSpeed(0, 0)
            motor.updateMotors() 
            print ('stop') 
            time.sleep(0.5)
            while  distance > OBSTACLE_NEAR:
              value = ads1015.read(0)
              distance = 14 / (value/1000 - 0.1)
              motor.setSpeed(-MAX_SPEED/2, MAX_SPEED/2)
              motor.updateMotors() 

        elif distance > OBSTACLE_NEAR:
            motor.setSpeed(MAX_SPEED/2, MAX_SPEED/2)
            print ('slow') 

        elif distance > OBSTACLE_FAR:
            motor.setSpeed(MAX_SPEED/2, MAX_SPEED/2)
            print ('half speed') 

        else:
            motor.setSpeed(MAX_SPEED, MAX_SPEED)
            print ('max speed') 

        motor.updateMotors() 
        
      finally:
        # Stop the motors, even if there is an exception
        # or the user presses Ctrl+C to kill the process.
        motors.setSpeeds(0, 0) 
        print ("program stopped!");
        
