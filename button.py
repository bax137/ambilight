#!/usr/bin/env python
import sys 
import RPi.GPIO as GPIO
import time
import os
 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, True)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, True)
GPIO.setup(14,GPIO.IN)
 
button_previous = 1
button_current = 1
brojac = 0
flag_pressed = 0
 
while True:
 
  button_current = GPIO.input(14);
  flag_pressed = button_previous + button_current
 
  if (not(flag_pressed)):
    brojac += 1
  else:
    brojac = 0
 
  if (button_current and (not button_previous)):
    print("Shutdown")
    os.system("shutdown -h now")
    GPIO.output(23, True)    
    GPIO.output(24, False)
 
  if ((not flag_pressed) and  brojac >= 100):
    print("Reset")
    os.system("shutdown -r now")
    GPIO.output(23, False)
    break
 
  button_previous = button_current
  time.sleep(0.03)
 
GPIO.cleanup()
