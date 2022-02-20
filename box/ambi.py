#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os,sys,time,logging,threading,requests,json
import spidev as SPI
sys.path.append("/home/pi/LCD_Module_code/RaspberryPi/python")
from lib import LCD_1inch28
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO
from datetime import datetime

######################
#       config       #
######################
rotation=-6
hyperhdr_url = "http://192.168.1.134:8090/json-rpc/"
fan_speed=90

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

def dispBackgroung(image):
    draw = ImageDraw.Draw(image)
    draw.arc((1,1,239,239),0, 360, fill =(0,0,255))
    draw.arc((2,2,238,238),0, 360, fill =(0,0,255))
    draw.arc((3,3,237,237),0, 360, fill =(0,0,255))
    return draw

def dispText(disp,textH, textM, text, colorTime = "PURPLE", colorText = "YELLOW"):
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = dispBackgroung(image)
    draw.text((51, 45), textH, fill = colorTime,font=Font3)
    draw.text((121, 45), textM, fill = colorTime,font=Font3)
    draw.text((50, 125), text, fill = colorText,font=Font4)
    disp.ShowImage(image.rotate(rotation))

class CurrentParams():
    def __init__(self):
        super(CurrentParams, self).__init__()

class Button(threading.Thread):
    def __init__(self):
        super(Button, self).__init__()

    def run(self):
        button_previous = 1
        button_current = 1
        brojac = 0
        flag_pressed = 0
        while True:
            button_current = GPIO.input(but_IN)
            flag_pressed = button_previous + button_current

            if (not(flag_pressed)):
                brojac += 1
            else:
                brojac = 0

            if (button_current and (not button_previous)):
                dispText(disp,"Shutdown","...........")
                print("Shutdown")
                os.system("shutdown -h now")
                GPIO.output(but_OUT1, True)
                GPIO.output(but_OUT2, False)

                disp.module_exit()
                #fan_pwm.stop()
                GPIO.cleanup()
                break

            if ((not flag_pressed) and  brojac >= 100):
                dispText(disp,"Reboot","...........")

                print("Reboot")
                os.system("Reboot -r now")
                GPIO.output(but_OUT1, False)
                disp.module_exit()
                #fan_pwm.stop()
                GPIO.cleanup()
                break

            button_previous = button_current

            time.sleep(0.03)

class Screen(threading.Thread):
    def __init__(self):
        super(Screen, self).__init__()
        self.text = ""
        self.text_color = "YELLOW"

    def run(self):
        step_sec=0
        while True:
            now = datetime.now()
            M=now.strftime("%M")
            H=""
            if step_sec==1:
                step_sec=0
                H = now.strftime("%H:")
            else:
                step_sec=1
                H = now.strftime("%H")
            dispText(disp,H,M,self.text,colorText=self.text_color)
            
            time.sleep(0.5)

class HyperHDR(threading.Thread):
    def __init__(self):
        super(HyperHDR, self).__init__()
        
    def run(self):
        step_sec=0
        while True:
            #HYPERHDR
            payload = json.dumps({
                "command": "serverinfo",
                "tan": 0
            })
            headers = {
                'Content-Type': 'application/json'
            }

            try:
                response = requests.request("POST", hyperhdr_url, headers=headers, data=payload)
                json_resp= json.loads(response.text)
                if (json_resp["success"] == True):
                    screen.text="HyperHDR ON"
                    screen.text_color="GREEN"
            except:
                screen.text = "HyperHDR OFF"
                screen.text_color = "RED"
            
            time.sleep(1)

if __name__ == "__main__":

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    ######################
    #       fan up       #
    ######################
    GPIO.setup(fan_PWM, GPIO.OUT)
    fan_pwm = GPIO.PWM(fan_PWM,25000)
    fan_pwm.start(fan_speed)
    #soft_pwm.ChangeDutyCycle(90)

    ######################
    #     init button    #
    ######################
    GPIO.setup(but_OUT1, GPIO.OUT)
    GPIO.output(but_OUT1, True)
    GPIO.setup(but_OUT2, GPIO.OUT)
    GPIO.output(but_OUT2, True)
    GPIO.setup(but_IN,GPIO.IN)

    ######################
    #     init screen    #
    ######################

    logging.basicConfig(level=logging.DEBUG)
    Font1 = ImageFont.truetype("/home/pi/Font/Font01.ttf",25)
    Font2 = ImageFont.truetype("/home/pi/Font/Font01.ttf",35)
    Font3 = ImageFont.truetype("/home/pi/Font/Font02.ttf",65)
    Font4 = ImageFont.truetype("/home/pi/Font/Font02.ttf",35)

    currentParams = CurrentParams()

    # display with hardware SPI:
    ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
    disp = LCD_1inch28.LCD_1inch28(spi=SPI.SpiDev(disp_bus, disp_device),spi_freq=10000000,rst=disp_RST,dc=disp_DC,bl=disp_BL)
    # Initialize library.
    disp.Init()
    disp.clear()

    screen = Screen()
    screen.start()
    
    # initialize display
    screen.text="Initialisaiton"

    button = Button()
    button.start()

    hyperHDR = HyperHDR()
    hyperHDR.start()

