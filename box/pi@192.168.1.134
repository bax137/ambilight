#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os,sys,time,logging
import spidev as SPI
sys.path.append("/home/pi/LCD_Module_code/RaspberryPi/python")
from lib import LCD_1inch28
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO
rotation=90

######################
#        pins        #
######################
#fan
fan_PWM=13
#display
disp_RST = 27
disp_DC = 25
disp_BL = 17
disp_bus = 1
disp_device = 0
#button
but_IN=14
but_OUT1=23
but_OUT2=24

def dispBackgroung(disp,image):
    # Clear display.
    disp.clear()
    # Create blank image for drawing.
    draw = ImageDraw.Draw(image)
    draw.arc((1,1,239,239),0, 360, fill =(0,0,255))
    draw.arc((2,2,238,238),0, 360, fill =(0,0,255))
    draw.arc((3,3,237,237),0, 360, fill =(0,0,255))
    return draw

def dispText(draw,text,position,color,font):
    return draw.text(position, text, fill = color,font=font)

def dispFS(disp,text1, text2):
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = dispBackgroung(disp,image)

    draw = dispText(draw,text1,(74, 150),"YELLOW",Font1)
    draw = dispText(draw,text2,(40, 50),(128,255,128),Font2)

    disp.ShowImage(image.rotate(rotation))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

######################
#       fan up       #
######################
GPIO.setup(fan_PWM, GPIO.OUT)
fan_pwm = GPIO.PWM(fan_PWM,25000)
fan_pwm.start(90)
#soft_pwm.ChangeDutyCycle(90)

######################
#     init button    #
######################
GPIO.setup(but_OUT1, GPIO.OUT)
GPIO.output(but_OUT1, True)
GPIO.setup(but_OUT2, GPIO.OUT)
GPIO.output(but_OUT2, True)
GPIO.setup(but_IN,GPIO.IN)
button_previous = 1
button_current = 1
brojac = 0
flag_pressed = 0

######################
#     init screen    #
######################

logging.basicConfig(level=logging.DEBUG)
Font1 = ImageFont.truetype("/home/pi/Font/Font01.ttf",25)
Font2 = ImageFont.truetype("/home/pi/Font/Font01.ttf",35)
Font3 = ImageFont.truetype("/home/pi/Font/Font02.ttf",32)

# display with hardware SPI:
''' Warning!!!Don't  creation of multiple displayer objects!!! '''
disp = LCD_1inch28.LCD_1inch28(spi=SPI.SpiDev(disp_bus, disp_device),spi_freq=10000000,rst=disp_RST,dc=disp_DC,bl=disp_BL)
# Initialize library.
disp.Init()

# initialize display
dispFS(disp,'INITIALISATION', '......')

while True:
    button_current = GPIO.input(but_IN)
    flag_pressed = button_previous + button_current

    if (not(flag_pressed)):
        brojac += 1
    else:
        brojac = 0

    if (button_current and (not button_previous)):
        dispFS(disp,'SHUTDOWN', '......')

        print("Shutdown")
        os.system("shutdown -h now")
        GPIO.output(but_OUT1, True)
        GPIO.output(but_OUT2, False)

    if ((not flag_pressed) and  brojac >= 100):
        dispFS(disp,'RESET', '......')

        print("Reset")
        os.system("shutdown -r now")
        GPIO.output(but_OUT1, False)
        break

    button_previous = button_current
    time.sleep(0.03)

disp.module_exit()
fan_pwm.stop()
GPIO.cleanup()