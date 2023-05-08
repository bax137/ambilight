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
webserver_ip = "192.168.1.134"
webserver_port = 8888
hue_ip = "192.168.1.100"
hue_auth_token = "UyUyQ0wu3TRdWKOC4SDK7VCum3O8LEOMpiQahvGF"
BACK_ON_COLOR = [(94,0,186),(45,0,89)]
BACK_SLEEP_COLOR = [(61,0,121),(28,0,55)]
TIME_ON_COLOR = (0,135,166)
TIME_SLEEP_COLOR = "PURPLE"
fan_speed=90
fan_speed_sleep=30

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


def dispBackgroung(image,a,b):
    draw = ImageDraw.Draw(image)
    #if animBackground.active == False:
    #    a = 0
    #    b = 360
    #else:
    #    draw.arc((1,3,237,239),b,a,fill="RED")

    draw.arc((1,1,239,239),a, b, fill = screen.bakground_color[0])
    draw.arc((2,2,238,238),a, b, fill = screen.bakground_color[0])
    draw.arc((3,3,237,237),a, b, fill = screen.bakground_color[0])
    draw.arc((4,4,236,236),a, b, fill = screen.bakground_color[1])
    draw.arc((5,5,235,235),a, b, fill = screen.bakground_color[0])
    draw.arc((6,6,234,234),a, b, fill = screen.bakground_color[0])
    draw.arc((7,7,233,233),a, b, fill = screen.bakground_color[0])
    return draw

class AnimBackground(threading.Thread):
    def __init__(self):
        super(AnimBackground, self).__init__()
        self.active = False

    def run(self):
        while True:
            if self.active == True:
                screen.a += 1
                if screen.a == 361:
                    screen.a = 0
                screen.b += 1
                if screen.b == 361:
                    screen.b = 0
                screen.refresh

            time.sleep(0.05)

class Screen():
    def __init__(self,disp):
        super(Screen, self).__init__()
        self.disp = disp
        self.textH = ""
        self.textM = ""
        self.text = ""
        self.time_color = TIME_SLEEP_COLOR
        self.text_color = "YELLOW"
        self.bakground_color = BACK_SLEEP_COLOR
        self.texti = [-1,-1,-1,-1]
        self.in_progress = False
        self.a = 0
        self.b = 360

    def refresh(self):    
        while self.in_progress == True:
            pass
        self.in_progress = True 
        image = Image.new("RGB", (self.disp.width, self.disp.height), "BLACK")
        draw = dispBackgroung(image,self.a,self.b)
        draw.text((48, 45), self.textH, fill = self.time_color,font=Font3)
        draw.text((133, 45), self.textM, fill = self.time_color,font=Font3)
        draw.text((50, 125), self.text, fill = self.text_color,font=Font4)
        position=[(80, 170),(105, 170),(130, 170),(155, 170)]
        instance_text = ""
        if hyperHDR.desired_status == 1:
            for i in range(0,4):
                instance_text = str(i)
                color = "RED"
                if self.texti[i] == 1:
                    color = "GREEN"
                elif self.texti[i] == -1:
                    instance_text = ""
                    color = "ORANGE"
                draw.text(position[i], instance_text, fill = color,font=Font4)
        self.disp.ShowImage(image.rotate(rotation))
        self.in_progress = False

class Button(threading.Thread):
    SLEEP_ON_DURATION = 0.5
    SLEEP_OFF_DURATION = 5

    def __init__(self):
        super(Button, self).__init__()
        self.sleep_led_status = False

    def run(self):
        button_previous = 1
        button_current = 1
        brojac = 0
        flag_pressed = 0
        now1 = datetime.now()
        while True:
            now2 = datetime.now()
            if hyperHDR.desired_status == 0:
                if self.sleep_led_status == False:
                    if (now2-now1).total_seconds() > self.SLEEP_OFF_DURATION:
                        GPIO.output(but_OUT1, True)
                        self.sleep_led_status = True
                        now1 = datetime.now()
                elif (now2-now1).total_seconds() > self.SLEEP_ON_DURATION:
                    GPIO.output(but_OUT1, False)
                    self.sleep_led_status = False
                    now1 = datetime.now()
            elif self.sleep_led_status == False:
                GPIO.output(but_OUT1, True)

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
                screen.text="...sleep..."
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
    
    #disable streaming for hue
    url = "http://"+hue_ip+"/api/"+hue_auth_token+"/groups/6"
    payload = json.dumps({
        "stream": {
        "active": False
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }

    while hyperHDR.status == 0:
        pass
    requests.request("GET", url, headers=headers, data=payload)

    #activate sound effect on leds box
    url = "http://"+hyperhdr_ip+":"+str(hyperhdr_port)+"/json-rpc/"
    url += "?request=%7B%22command%22:%22instance%22,%22subcommand%22:%22switchTo%22,%22instance%22:3%7D"
    url += "&request=%7B%22command%22:%22effect%22,%22effect%22:%7B%22name%22:\"Music: stereo for LED strip (MULTI COLOR)%22%7D,%22priority%22:50,%22origin%22:%22AmbiBox%22%7D"
    url += "&request=%7B%22command%22:%22componentstate%22,%22componentstate%22:%7B%22component%22:%22V4L%22,%22state%22:false%7D%7D"

    payload = ""
    headers = {}
    requests.request("GET", url, headers=headers, data=payload)

def hyperHDRSubscribe():
    while hyperHDR.status == 0:
            pass
    ws.send("""{
        "command":"serverinfo",
        "subscribe":["instance-update"],
        "tan":1
    }""")

def stopHyperHDR():
    subscriptionThread.active = False
    hyperHDR.desired_status = 0
    os.system("systemctl stop hyperhdr@root")
    hyperHDR.status = 0
    screen.bakground_color = BACK_SLEEP_COLOR
    screen.time_color = TIME_SLEEP_COLOR
    fan_pwm.ChangeDutyCycle(fan_speed_sleep)

def startHyperHDR():
    hyperHDR.desired_status = 1
    os.system("systemctl start hyperhdr@root")
    hyperHDRInit()
    subscriptionThread.active = True
    screen.bakground_color = BACK_ON_COLOR
    screen.time_color = TIME_ON_COLOR
    fan_pwm.ChangeDutyCycle(fan_speed)

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

class WebServer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        response = 0
        message = ''
        if self.path.endswith('/hyperhdr'):
            post_body_json = json.loads(post_body)
            if "command" in post_body_json:
                if post_body_json["command"] == "stop":
                    stopHyperHDR()
                    response = 200
                    message = message = '{"result":"HyperHDR Stopped"}'
                elif post_body_json["command"] == "start":
                    startHyperHDR()
                    response = 200
                    message = '{"result":"HyperHDR Started"}'
                else:
                    response = 400
                    message = '{"error":"Unknown command"}'
            else:
                response = 400
                message = 'Unknonw field'
        elif self.path.endswith('/pi'):
            post_body_json = json.loads(post_body)
            if "command" in post_body_json:
                if post_body_json["command"] == "shutdown":
                    piShutdown()
                    response = 200
                    message = '{"result":"PI shutdowned"}'
                else:
                    response = 400
                    message = '{"error":"Unknown command"}'
            else:
                response = 400
                message = '{"error":"Unknown field"}'
        else:
            response = 404
            message = '{"error":"command not found"}'

        self.send_response(response)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(message,"utf8"))

    def do_GET(self):
        response = 0
        message = ""
        if self.path.endswith('/hyperhdr'):
            response = 200
            if hyperHDR.status == 1:
                message = '{"is_active":"true"}'
            else: 
                message = '{"is_active":"false"}'
                response = 200
        elif self.path.endswith('/status'):
            message = '{"result":"ok"}'
            response = 200
        else:
            response = 404
            message = '{"error":"command not found"}'
        
        self.send_response(response)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(message,"utf8"))

class WebServerThread(threading.Thread):
    def __init__(self):
        super(WebServerThread, self).__init__()
    
    def run(self):
        #asyncio.run(main())
        webServer = HTTPServer((webserver_ip, webserver_port), WebServer)
        webServer.serve_forever()

class SubscriptionThread(threading.Thread):
    def __init__(self):
        super(SubscriptionThread, self).__init__()
        self.active = True

    def run(self):
        while True:
            if self.active == True and hyperHDR.status == 1:
                ws.run_forever()

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

    #animBackground = AnimBackground()
    #animBackground.start()

    screen.text="Initialisaiton"
    screen.refresh()

    button = Button()
    button.start()

    hyperHDR.desired_status = 1
    hyperHDR.screen_started = 1

    webServerThread = WebServerThread()
    webServerThread.start()

    ws = websocket.WebSocketApp("ws://"+hyperhdr_ip+":"+str(hyperhdr_port)+"/json-rpc",
                        on_open=on_open,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_close)
    
    #subscription to hyperHDR updates
    subscriptionThread = SubscriptionThread()
    subscriptionThread.start()

    startHyperHDR()