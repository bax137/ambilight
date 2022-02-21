#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
#from multiprocessing.connection import wait
import os,sys,time,logging,threading,requests,json,websocket #,websockets,asyncio
import _thread as thread
import spidev as SPI
sys.path.append("/home/pi/LCD_Module_code/RaspberryPi/python")
from lib import LCD_1inch28
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO
from datetime import datetime


from http.server import BaseHTTPRequestHandler, HTTPServer

######################
#       config       #
######################
rotation=-6
hyperhdr_ip = "localhost"
hyperhdr_port = 8090
hyperhdr_url = "http://"+hyperhdr_ip+":"+str(hyperhdr_port)+"/json-rpc/"
webserver_port = 8888

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

Font1 = ImageFont.truetype("/home/pi/Font/Font01.ttf",25)
Font2 = ImageFont.truetype("/home/pi/Font/Font01.ttf",35)
Font3 = ImageFont.truetype("/home/pi/Font/Font02.ttf",65)
Font4 = ImageFont.truetype("/home/pi/Font/Font02.ttf",35)


def dispBackgroung(image):
    draw = ImageDraw.Draw(image)
    draw.arc((1,1,239,239),0, 360, fill =(0,0,255))
    draw.arc((2,2,238,238),0, 360, fill =(0,0,255))
    draw.arc((3,3,237,237),0, 360, fill =(0,0,255))
    return draw

class Screen():
    def __init__(self,disp):
        super(Screen, self).__init__()
        self.disp = disp
        self.textH = ""
        self.textM = ""
        self.text = ""
        self.time_color = "PURPLE"
        self.text_color = "YELLOW"
        self.texti = [-1,-1,-1,-1]
        self.in_progress = False 

    def refresh(self):    
        image = Image.new("RGB", (self.disp.width, self.disp.height), "BLACK")
        draw = dispBackgroung(image)
        draw.text((48, 45), self.textH, fill = self.time_color,font=Font3)
        draw.text((133, 45), self.textM, fill = self.time_color,font=Font3)
        draw.text((50, 125), self.text, fill = self.text_color,font=Font4)
        position=[(80, 170),(105, 170),(130, 170),(155, 170)]
        if hyperHDR.desired_status == 1:
            for i in range(0,4):
                color = "RED"
                if self.texti[i] == 1:
                    color = "GREEN"
                elif self.texti[i] == -1:
                    color = "ORANGE"
                draw.text(position[i], str(i), fill = color,font=Font4)
        while self.in_progress == True:
            pass
        self.in_progress = True 
        self.disp.ShowImage(image.rotate(rotation))
        self.in_progress = False

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
                if hyperHDR.desired_status == 1:
                    stopHyperHDR()
                else:
                    startHyperHDR()
                break
            if ((not flag_pressed) and  brojac >= 100):
                piShutdown()
                break

            button_previous = button_current

            time.sleep(0.03)

class Clock(threading.Thread):
    def __init__(self):
        super(Clock, self).__init__()
        self.stop = False

    def run(self):
        step_sec=0
        while self.stop == False:
            now = datetime.now()
            M=now.strftime("%M")
            H=""
            if step_sec==1:
                step_sec=0
                H = now.strftime("%H:")
            else:
                step_sec=1
                H = now.strftime("%H")
            screen.textH = H
            screen.textM = M
            screen.refresh()            
            time.sleep(0.5)

class HyperHDR(threading.Thread):
    def __init__(self):
        super(HyperHDR, self).__init__()
        self.init_status = 0
        self.status = 0
        self.desired_status = 0
        self.screen_started = 0
        
    def run(self):
        while True:
            #HYPERHDR
            if self.desired_status == 1:
                payload = json.dumps({
                    "command": "serverinfo",
                })
                headers = {
                    'Content-Type': 'application/json'
                }

                text = "HyperHDR OFF"
                text_color = "RED"
                try:
                    response = requests.request("POST", hyperhdr_url, headers=headers, data=payload)
                    json_resp= json.loads(response.text)
                    if (json_resp["success"] == True):
                        text_color="GREEN"
                        text="HyperHDR ON"
                        self.status = 1
                        self.init_status = 1
                    else:
                        screen.texti = [-1,-1,-1,-1]
                        text_color="ORANGE"
                        text="HyperHDR..."
                except:
                    self.status = 0
                    screen.texti = [-1,-1,-1,-1]
                
                if self.init_status == 1:
                    screen.text_color=text_color
                    screen.text=text
                    screen.refresh()
            elif self.screen_started:
                screen.text_color="BLUE"
                screen.text="sleep..."
                screen.refresh()
            time.sleep(1)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        print("### open ###")
        hyperHDRSubscribe()

    thread.start_new_thread(run, ())

def on_message(ws, message):
    #print(message)
    json_message = json.loads(message)
    if 'data' in json_message:
        for i in range(0,4):
            if 'instance' in json_message["data"][i]:
                if json_message["data"][i]["running"] == True:
                    screen.texti[i] = 1
                else:
                    screen.texti[i] = 0
        screen.refresh()

    if 'info' in json_message:
        if 'instance' in json_message["info"]:
            for i in range(0,4):
                if 'instance' in json_message["info"]["instance"][i]:
                    if json_message["info"]["instance"][i]["running"] == True:
                        screen.texti[i] = 1
                    else:
                        screen.texti[i] = 0
            screen.refresh()

def hyperHDRInit():
    i = 0
    text = ""
    while hyperHDR.init_status == 0:
        if i == 0:
            text = "hyperHDR"
            i = 1
        else:
            text = ""
            i = 0
        screen.text_color = "YELLOW"
        screen.text = text
        screen.refresh()

        time.sleep(0.5)

    #activate sound effect on leds box
    url = "http://"+hyperhdr_ip+":"+str(hyperhdr_port)+"/json-rpc/"
    url += "?request=%7B%22command%22:%22instance%22,%22subcommand%22:%22switchTo%22,%22instance%22:3%7D"
    url += "&request=%7B%22command%22:%22effect%22,%22effect%22:%7B%22name%22:\"Music: stereo for LED strip (MULTI COLOR)%22%7D,%22priority%22:50,%22origin%22:%22AmbiBox%22%7D"
    url += "&request=%7B%22command%22:%22componentstate%22,%22componentstate%22:%7B%22component%22:%22V4L%22,%22state%22:false%7D%7D"

    payload = ""
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

def hyperHDRSubscribe():
    ws.send("""{
        "command":"serverinfo",
        "subscribe":["instance-update"],
        "tan":1
    }""")

def stopHyperHDR():
    hyperHDR.desired_status = 0
    os.system("systemctl stop hyperhdr@root")

def startHyperHDR():
    hyperHDR.desired_status = 1
    os.system("systemctl start hyperhdr@root")
    hyperHDRInit()

def piShutdown():
    clock.stop = True
    screen.textH = ""
    screen.textM = ""
    screen.texti = [-1,-1,-1,-1]
    screen.text_color = "YELLOW"
    screen.text = "shutdown..."
    screen.refresh()
    GPIO.output(but_OUT1, False)
    GPIO.output(but_OUT2, False)
    disp.module_exit()
    #fan_pwm.stop()
    GPIO.cleanup()
    os.system("sudo shutdown -h now")


#async def command(websocket):
#    async for message in websocket:
#        if message == "stop":
#            stopHyperHDR()
#            await websocket.send("HyperHDR Stopped")
#        elif message == "start":
#            startHyperHDR()
#            await websocket.send("HyperHDR Started")
#        else:
#            await websocket.send("unkown command")

#async def main():
#    async with websockets.serve(command, "localhost",  8765):
#        await asyncio.Future()

#class WebServer(threading.Thread):
#    def __init__(self):
#        super(WebServer, self).__init__()
#    
#    def run(self):
#            asyncio.run(main())

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('/hyperhdr/stop'):
            stopHyperHDR()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'HyperHDR Stopped')
        elif self.path.endswith('/hyperhdr/start'):
            startHyperHDR()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'HyperHDR Started')
        elif self.path.endswith('/pi/shutdown'):
            piShutdown()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'PI shutdowned')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Unknown command') 

class WebServerThread(threading.Thread):
    def __init__(self):
        super(WebServerThread, self).__init__()
    
    def run(self):
        #asyncio.run(main())
        webServer = HTTPServer(("localhost", webserver_port), WebServer)
        webServer.serve_forever()

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

    logging.basicConfig(level=logging.WARNING)


    hyperHDR = HyperHDR()
    hyperHDR.start()

    # display with hardware SPI:
    ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
    disp = LCD_1inch28.LCD_1inch28(spi=SPI.SpiDev(disp_bus, disp_device),spi_freq=10000000,rst=disp_RST,dc=disp_DC,bl=disp_BL)
    # Initialize library.
    disp.Init()
    disp.clear()

    screen = Screen(disp)
    clock = Clock()
    clock.start()

    screen.text="Initialisaiton"
    screen.refresh()

    button = Button()
    button.start()

    hyperHDR.desired_status = 1
    hyperHDR.screen_started = 1

    webServerThread = WebServerThread()
    webServerThread.start()

    hyperHDRInit()

   #subscription to hyperHDR updates
    ws = websocket.WebSocketApp("ws://"+hyperhdr_ip+":"+str(hyperhdr_port)+"/json-rpc",
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

    while True:
        ws.run_forever()