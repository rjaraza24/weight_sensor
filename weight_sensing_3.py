#! /usr/bin/python2
#from getmac import get_mac_address
from uuid import getnode as get_mac
from urllib.parse import urlencode
#import urllib.parse
import pycurl
import time
import sys
from time import gmtime, strftime
EMULATE_HX711=False

import requests
import json

referenceUnit = 108

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711





import urllib.request
def connect():
    try:
        urllib.request.urlopen('http://google.com') #Python 3.x
        return True
    except:
        return False
print( 'connected' if connect() else 'no internet!' )
        



mac = get_mac()
#mac_1 =  (" %s_1 "%(str(mac)))
#mac_2 =  (" %s_2 "%(str(mac)))
#mac_3 =  (" %s_3 "%(str(mac)))

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin BCM 18 to be an input pin and set initial value to be pulled low (off)



def cleanAndExit():
    print ("Cleaning...")
    if not EMULATE_HX711:
     GPIO.cleanup()
     print ("Bye!")
    sys.exit()


hx1 = HX711(3, 2) 
hx2 = HX711(15, 14)
hx3 = HX711(24, 23)

hx1.set_reading_format("MSB", "MSB")
hx2.set_reading_format("MSB", "MSB")
hx3.set_reading_format("MSB", "MSB")

hx1.set_reference_unit(referenceUnit)
hx2.set_reference_unit(referenceUnit)
hx3.set_reference_unit(referenceUnit)

hx1.reset()
hx1.tare()
hx2.reset()
hx2.tare()
hx3.reset()
hx3.tare()
status = 0
deviceID_1= 1
tolp = 20
toln = -20
btn = 0
rep = 0
chg = 0
#url = 'https://offtake-test.foapplication.com/api/update'
url = 'https://offtake-test.foapplication.com/api/v1/update'

#url = 'https://www.code-learner.com/post/'
while True:
 try:
  #connect()
  print( 'connected' if connect() else 'no internet!' )
   # init previous values
  prev_val1 = 0
  prev_val2 = 0
  prev_val3 = 0

  if GPIO.input(18) == GPIO.HIGH:
   #print("Button is on, replenish time")
   rep = 1
   print("Button is on")
   time.sleep(1)

  elif GPIO.input(18) == GPIO.LOW:
   val1 = round(hx1.get_weight(5),1)
   val2 = round(hx2.get_weight(5),1)
   val3 = round(hx3.get_weight(5),1)

   # compare if current value is equal to previous value, add mo ung allowance
   if (prev_val1 - tolp) <= val1 and (prev_val1 + tolp) >= val1:
     # set mo ung current value as previous val, para un ung value sa next loop

     # kung ung weight nung previous value is same sa current value set mo as 0
     val1 = 0
     prev_val1 = val1
     chg =0

   if (prev_val2 - tolp) <= val2 and (prev_val2 + tolp) >= val2:
     val2 = 0
     prev_val2 = val2
     chg=0
   if (prev_val3 - tolp) <= val3 and (prev_val3 + tolp) >= val3:
     val3 = 0
     prev_val3 = val3
     chg=0

   if (prev_val3 + val3) <= toln or (prev_val3 + val3) >= tolp:
     prev_val3 = val3
     chg = 1
     print("val3")

   if (prev_val2 + val2) <= toln or (prev_val2 + val2) >= tolp:
     prev_val2 = val2
     chg = 1
     print("val2")

   if (prev_val1 + val1) <= toln or (prev_val1 + val1) >= tolp:
     prev_val1 = val1
#     chg = 1
     print("val1")

   rtc = time.strftime("%Y-%m-%d %H:%M")
   crl = pycurl.Curl()
   minutes = strftime("%M", gmtime())
   print ("id: %s , 1: %s ,  2: %s ,  3: %s , DateTime : %s, Status: %s" %(mac,val1,val2,val3,rtc,btn))
   #print ("1: %s ,  2: %s ,  3: %s , Status: %s" %(val1,val2,val3,btn))
   print("Button is off")


   if (rep == 1 and chg == 1):
    print("r1")
    btn = 1
    #chg = 0
    if ((int(minutes)%2 == 0 or int(minutes) == 0) and connect()) :
      #chg = 0
      if(status == 0):
        data = {
            'panel1' : prev_val1,
            'panel2' : prev_val2,
            'panel3' : prev_val3,
            'device_id' : mac,
            'status' : btn
            }


        ss = open("ssLog.txt", 'a')
        ss.write("Device_ID: %s , Panel1: %s , Panel2: %s , Panel3: %s ,DateTime: %s ,  Status: %s " %(mac,val1,val2,val3,rtc, btn) + '\n')
        print ("File Ammended")
        ss.close()
        print ("File Closed")
        time.sleep(1)
        print ("Device_ID: %s , Panel1: %s , Panel2: %s , Panel3: %s , DateTime : %s, Status: %s" %(mac,val1,val2,val3,rtc,btn))
        crl.setopt(crl.URL, url)
        pf = urlencode(data)
        #pf = urllib.parse.quote(data)
        crl.setopt(crl.POSTFIELDS, pf)
        crl.perform()
        crl.close()
        status = 1
        rep = 0
        time.sleep(0.5)
        chg = 0
        #val1 = 0
        #val2 = 0
        #val3 = 0
        #prev_val1 = 0
        #prev_val2 = 0
        #prev_val3 = 0

        hx1.reset()
        hx1.tare()
        hx2.reset()
        hx2.tare()
        hx3.reset()
        hx3.tare()
#        hx1.power_down()
#        hx1.power_up()
#        hx2.power_down()
#        hx2.power_up()
#        hx3.power_down()
#        hx3.power_up()

    else:
        status = 0
        #print "Message Sent"
        #chg = 0

   elif (rep == 0 and chg == 1):
    print("r0")
    btn = 0
    rep = 0
    if ((int(minutes)%2 == 0 or int(minutes) == 0) and connect()) :

      #chg = 0
      if(status == 0):
        data = {
            'panel1' : prev_val1,
            'panel2' : prev_val2,
            'panel3' : prev_val3,
          'device_id' : mac,
            'status' : btn
            }


        ss = open("ssLog.txt", 'a')
        ss.write("id: %s ,  1: %s ,  2: %s ,  3: %s , DateTime: %s ,  Status: %s " %(mac,val1,val2,val3,rtc, btn) + '\n')
        print ("File Ammended")
        ss.close()
        print ("File Closed")
        time.sleep(1)
        print (" ID: %s ,  1: %s ,  2: %s ,  3: %s , DateTime : %s, Status: %s" %(mac,val1,val2,val3,rtc,btn))
        crl.setopt(crl.URL, url)
        pf = urlencode(data)
        #pf = urllib.parse.quote(data)
        crl.setopt(crl.POSTFIELDS, pf)
        crl.perform()
        crl.close()
        status = 1
        time.sleep(0.5)
        #chg = 0
        #val1 = 0
        #val2 = 0
        #val3 = 0
        #prev_val1 = 0
        #prev_val2 = 0
        #prev_val3 = 0
        hx1.reset()
        hx1.tare()
        hx2.reset()
        hx2.tare()
        hx3.reset()
        hx3.tare()
 #       hx1.power_down()
 #       hx1.power_up()
 #       hx2.power_down()
 #       hx2.power_up()
 #       hx3.power_down()
 #       hx3.power_up()
    else:
        status = 0
        #print "Message Sent"
        #chg = 0 
   hx1.power_down()
   hx1.power_up()
   hx2.power_down()
   hx2.power_up()
   hx3.power_down()
   hx3.power_up()
   time.sleep(0.5)
 except (KeyboardInterrupt, SystemExit):
  cleanAndExit()
