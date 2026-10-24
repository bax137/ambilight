import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.OUT)
soft_pwm = GPIO.PWM(13,25000)
soft_pwm.start(0)
soft_pwm.ChangeDutyCycle(90)
time.sleep(10)

soft_pwm.stop()
GPIO.cleanup()
