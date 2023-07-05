import eel
import pyodbc 
import re
import requests
import json 
import cv2
from discordwebhook import Discord
DATABASE_SERVER = "IP_ADDRESS" #MSSQL IP/Hostname
DATABASE_INSTANCE = "PAYAMGOSTAR2" #MSSQL Database instance
DATABASE_NAME = "PayamGostar2" #MSSQL Database name
SQL_USERNAME = "sa" #MSSQL Username
SQL_PASSWORD = "PASSWORD" #MSSQL Password
delaytimer = 7 #timer to reload the page for new users
normal_sales_ID = "2A944817-A89C-4307-90A8-9449F6047AD8" #ID of normal transactions
amani_sales_ID = "DF577FCA-D1A8-4A4F-9746-095E1E6594E5" #ID of amani transactions
discord = Discord(url="REPLACE_WISH_WEBHOOK_URL") #Discord Webhook address
conn = pyodbc.connect('Driver={SQL Server};'
                      f'Server={DATABASE_SERVER}\{DATABASE_INSTANCE};'
                      f'Database={DATABASE_NAME};'
                      f'UID={SQL_USERNAME};'
                      f'PWD={SQL_PASSWORD};')
cursor = conn.cursor()
hix = 0     

def selfie():
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
                filename = f"X:\{rname}-{opr}.jpg"
                print(f"File {rname}-{opr}.jpg written!")
                cv2.imwrite(filename,camera_capture)
                del(camera)

def payment():
    global payment_failed_reason
    eel.loading()
    #get token

    url = "https://idn.seppay.ir/connect/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic cm9jbGllbnQ6c2VjcmV0'}
    raw_data = 'grant_type=password&username=REPLACE_WITH_USERNAME&password=REPLACE_WITH_PASSWORD&scope=SepCentralPcPos openid'
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
        "TerminalID": "21312421",
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
        eel.sleep(delaytimer)
        eel.refreshPage()
        handleinput()
    else:
        discord.post(content=f"پرداخت موفق برای {rname} شماره حواله {opr} با مبلغ {pardakht} ریال")
        eel.addText("لطفا به باسکول مراجعه نمایید")
        eel.completed()
        eel.sleep(delaytimer)
        eel.refreshPage()
        #####scan
        #eel.addText("آیا قبلا مدارک خود را در این شرکت اسکن نموده اید؟")
        #eel.waitinput()
        #eel.enablebuttons()

        
eel.init('web')                     # Give folder containing web files

@eel.expose                         # Expose this function to Javascript
def handleinput(name):
    global hix
    global x
    global opr
    global rname
    global pardakht
    hix += 1
    if hix == 1:
        rname = name
        print(f"rname is {rname}")
    if hix == 2:
        opr = name
        print(f"opr is {opr}")
    if hix == 3:
        momayez = name
        print(f"momayez is {momayez}")
        if not momayez:
            print("Momayez is empty, not doing anything")
        else:
            print("Momayez has value, I'm gonna combine them rn")
            opr = (f"{opr}/{momayez}")
        hix = 0 #reset variable
        print(f"number is {opr}")
        conn = pyodbc.connect('Driver={SQL Server};'
                      f'Server={DATABASE_SERVER}\{DATABASE_INSTANCE};'
                      f'Database={DATABASE_NAME};'
                      f'UID={SQL_USERNAME};'
                      f'PWD={SQL_PASSWORD};')
        cursor = conn.cursor()
        results = cursor.execute(f"SELECT Id, InventoryId FROM InventoryTransaction WHERE Number = '{opr}'")
        for i in cursor:
            s = i
        try: s
        except NameError:{
            print("ERROR! ITEM NOT FOUND!"),
            eel.addText("حواله یافت نشد. لطفا شماره حواله را برسی و مجدد تلاش نمایید"),
            eel.error(),
            eel.sleep(delaytimer),
            eel.refreshPage()
        }
        if s[1] == normal_sales_ID: #detect type of transaction (normal, in this case)
            results = cursor.execute(f"SELECT CrmProperty2, CrmProperty12 FROM CrmObjectExtendedProperty WHERE (CrmObjectId = '{s[0]}')")
            for i in cursor:
                x = i
            cam = cv2.VideoCapture(0)
            #find payment value from string
            pardakht = x[1]
            #extract value from string
            if rname == x[0]:
                #selfie()
                discord.post(content=f"احراز هویت {rname} شماره حواله {opr} با موفقیت انجام شد")
                eel.addText(f"مبلغ پرداختی شما {pardakht} ریال میباشد")
                payment() #initiate payment
        if s[1] == amani_sales_ID: #detect type of transaction (amani, in this case)
            results = cursor.execute(f"SELECT CrmProperty4, CrmProperty8 FROM CrmObjectExtendedProperty WHERE (CrmObjectId = '{s[0]}')")
            for i in cursor:
                x = i
            cam = cv2.VideoCapture(0)
            #find payment value from string
            pardakht = x[1]
            #extract value from string
            if rname == x[0]:
                #selfie()
                discord.post(content=f"احراز هویت {rname} شماره حواله {opr} با موفقیت انجام شد")
                eel.addText(f"مبلغ پرداختی شما {pardakht} ریال میباشد")
                payment() #initiate payment
            
                
        else:
            #message = f"اطلاعات مربوط به کاربر {rname} با شماره حواله {opr} در سیستم یافت نشد و یا اطلاعات اشتباه وارد شده است"
            #url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
            #print(requests.get(url).json())
            eel.addText("حواله به نام شما نیست. لطفا ابتدا حواله را به نام کرده و سپس مجدد تلاش نمایید")
            eel.error()
            eel.sleep(delaytimer)
            eel.refreshPage()
        print("passed main sections")
    else:
        print(hix)
# Unused code from previous versions
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
                eel.sleep(delaytimer)
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
                filename = f"X:\{rname}-{opr}.jpg"
                print(f"File {rname}-{opr}.jpg written!")
                cv2.imwrite(filename,camera_capture)
                del(camera)
                eel.addText("مدارک شما با موفقیت اسکن شد، لطفا به باسکول مراجعه نمایید")
                discord.post(content=f"اسکن مدارک  برای {rname} با موفقیت انجام و فرایند احراز هویت تکمیل گردید")
                eel.completed()
                eel.sleep(delaytimer)
                eel.refreshPage()


   

eel.start("index.html", mode='chrome', cmdline_args=['--start-fullscreen', '--no-sandbox', '--kiosk',  '--disable-pinch'])
#eel.start('index.html')    # Start
