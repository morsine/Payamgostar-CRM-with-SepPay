import eel
from zeep import helpers
import re
from zeep import Client
from zeep.transports import Transport
from zeep import helpers
from lxml import etree
import requests
import json
from zeep.plugins import HistoryPlugin
from zeep.helpers import serialize_object
import PySimpleGUI as sg    
import cv2
import os
import os.path
import time
from discordwebhook import Discord
discord = Discord(url="REPLACE_WITH_DISCORD_WEBHOOK_URL")

x = 0     
        
        
eel.init('web')                     # Give folder containing web files

@eel.expose                         # Expose this function to Javascript
def handleinput(name):
    global x
    global opr
    global rname
    global pardakht
    x = x + 1
    if x == 1:
        rname = name
        print(rname)
    if x == 2:
        opr = name
        print(opr)
        x = 0 #reset variable
        print(f"number is {opr}")
        cam = cv2.VideoCapture(0)
        history = HistoryPlugin()
        #gui theme
        sg.theme('Topanga')
        #wsdl information
        wsdl = "http://192.168.3.10/services/api/iopportunity.svc?wsdl"
        client = Client(wsdl, plugins=[history])
        #convert arabic characters to persian
        rname = name.replace("ي", "ی")
        rname = name.replace("ك", "ک")
        #request to be sent to API
        request_data = {
            'userName': 'admin',
            'password': 'crm_admin_password',
            'typeKey': '',
            'query': f'Subject=="{opr}"'
            ''
        }
        #message = f"کاربر {rname} حواله {opr} در حال احراز هویت"
        #url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        #print(requests.get(url).json())
        result = client.service.SearchOpportunity(**request_data)
        result_dict = helpers.serialize_object(result, target_cls=dict)
        result_str = str(result_dict)
        #find payment value from string
        hazine = re.search("kharjeanbar', 'Value': '(.+?)'}", result_str)
        #extract value from string
        if hazine:
            pardakht = hazine.group(1)
        print(result_str) #debug
        if result_str.find(f"'UserKey': 'opportunityowner', 'Value': '{rname}'") != -1:
            #if user owns the opportunity
            #print smt
            file_exists = os.path.exists(f"Z:\{opr}.docx")
            if file_exists == True:
                print("Printer activity...")
                os.startfile(f"Z:\{opr}.docx", "print")
                discord.post(content=f"احراز هویت {rname} شماره حواله {opr} با موفقیت انجام شد")
                eel.addText("حواله یافت شد. در حال پرینت فاکتور خرج انبار")
            else:
                #print(requests.get(url).json())
                eel.addText("فاکتور خرج انبار شما در سیستم موجود نیست. لطفا با واحد اداری کارخانه تماس بگیرید")
                discord.post(content=f"فاکتور خرج انبار {rname} شماره حواله {opr} در سیستم موجود نیست. لطفا برسی گردد")
                eel.error()
                eel.sleep(5)
                eel.refreshPage()
                handleinput()
                
            eel.addText(f"مبلغ پرداختی شما {pardakht} ریال میباشد")
            
            payment()
            
                
        else:
            #message = f"اطلاعات مربوط به کاربر {rname} با شماره حواله {opr} در سیستم یافت نشد و یا اطلاعات اشتباه وارد شده است"
            #url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
            #print(requests.get(url).json())
            eel.addText("اطلاعات وارد شده صحیح نمیباشد و یا حواله به نام شما نیست")
            eel.error()
            eel.sleep(5)
            eel.refreshPage()
        print("passed main sections")
    else:
        print(x)
@eel.expose
def notscanned():
                eel.enablebuttons()
                eel.addText("خیر")
                eel.addText("لطفا ابتدا مدارک خود را در کادر مشخص شده قرار دهید و سپس دکمه ی اسکن را لمس کنید")
                eel.enableshutter()
                eel.waitinput()
@eel.expose
def alreadyscanned():
                eel.enablebuttons()
                eel.addText("بله")
                eel.addText("لطفا جهت ادامه فرایند به باسکول مراجعه نمایید")
                discord.post(content=f"احراز هویت برای {rname} با شماره حواله {opr} با وضعیت مدارک از قبل اسکن شده تکمیل گردید")
                eel.completed()
                eel.sleep(5)
                eel.refreshPage()

@eel.expose
def scan():
                eel.enableshutter() #hide the button!
                eel.loading()
                camera_port = 0 
                ramp_frames = 30 
                camera = cv2.VideoCapture(camera_port)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                def get_image():
                   retval, im = camera.read()
                   return im 
                for i in range(ramp_frames):
                  temp = camera.read()
                camera_capture = get_image()
                filename = f"X:\{opr}.jpg"
                print(f"File {opr}.jpg written!")
                cv2.imwrite(filename,camera_capture)
                del(camera)
                eel.addText("مدارک شما با موفقیت اسکن شد، لطفا به باسکول مراجعه نمایید")
                discord.post(content=f"اسکن مدارک جهت شماره حواله {opr} برای {rname} با موفقیت انجام و فرایند احراز هویت تکمیل گردید")
                eel.completed()
                eel.sleep(5)
                eel.refreshPage()

def payment():
    global payment_failed_reason
    eel.loading()
    #get token

    url = "https://idn.seppay.ir/connect/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic cm9jbGllbnQ6c2VjcmV0'}
    raw_data = 'grant_type=password&username=SepPay_Username&password=SepPay_Password&scope=SepCentralPcPos openid'
    response = requests.post(url, data=raw_data, headers=headers)
 
    print("Status code: ", response.status_code)
    print("Printing Entire Post Request")
    print(response.json())

    result_str = str(response.json())
    token = re.search(r"access_token': '(.*?)', 'expires_in", result_str).group(1)
    print(f"the token is {token}") #debug.. meh idk how to code

    #get identifier

    url = "https://cpcpos.seppay.ir/v1/PcPosTransaction/ReciveIdentifier"
    iden = {
        'Authorization': f'bearer {token}'
    }
    idenresponse = requests.post(url, headers=iden)
    iden_str = str(idenresponse.json())
    identifier = re.search(r"Identifier': '(.*?)'", iden_str).group(1)
    print (identifier)

    #post payment value

    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'bearer {token}'
    }
    payment_body = {
        "TerminalID": "REPLACE_WITH_TERMINAL_ID_OF_POS_DEVICE",
        "Amount": f"{pardakht}",
        "AccountType": 0,
        "ResNum": "1234",
        "Identifier": f"{identifier}",
        "TotalAmount": "10000",
        "userNotifiable":{
        "FooterMessage":"null",
        "PrintItems":[
            {
                "Item":f"{rname}",
                "Value":f"{opr}",
                "Alignment":1,
                "ReceiptType":2
            }
        ]
    },
    "TransactionType":0
    }
    url = "https://cpcpos.seppay.ir/v1/PcPosTransaction/StartPayment"
    eel.addText("لطفا کارت خود را بکشید")
    eel.waitinput()
    payment = requests.post(url, data=json.dumps(payment_body), headers=payment_headers)
    print("Status code: ", payment.status_code)
    print("Printing Entire Post Request")
    print(payment.json())
    result_str = str(payment.json())
    print(result_str)
    payment_results = re.search(r"IsSuccess': (.*?),", result_str).group(1)
    print(f"Payment status is {payment_results}")
    if payment_results == "False":
        print("Payment error")
        payment_failed_reason = re.search(r"'ErrorDescription': '(.*?)'", result_str).group(1)
        discord.post(content=f"پرداخت ناموفق مربوط به حواله {opr} برای {rname} به علت {payment_failed_reason} با مبلغ {pardakht} ریال")
        eel.addText(f"پرداخت ناموفق به علت {payment_failed_reason}")
        eel.error()
        eel.sleep(5)
        eel.refreshPage()
        handleinput()
    else:
        discord.post(content=f"پرداخت موفق برای {rname} شماره حواله {opr} با مبلغ {pardakht} ریال")
            
        #scan
        eel.addText("آیا قبلا مدارک خود را در این شرکت اسکن نموده اید؟")
        eel.waitinput()
        eel.enablebuttons()
   

eel.start("index.html", mode='chrome', cmdline_args=['--start-fullscreen', '--no-sandbox', '--kiosk',  '--disable-pinch'])
#eel.start('index.html')    # Start
