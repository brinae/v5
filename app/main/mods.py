import logging
import sqlite3, hashlib, os
import Adyen
import json
import uuid
from main.config import *
import requests

def adyen_modifications(modType, pspReference, modAmount, currency, modReference):
    global pspRef
    pspRef = pspReference
    adyen = Adyen.Adyen()
    platform = "test"
    xapikey = get_adyen_api_key()
    merchant_account = get_adyen_merchant_account()

    headers = {
        'X-API-Key': xapikey,
        'Content-Type': 'application/json'
    }
    

    modAmount = modAmount.replace('.', '')
    request = {}
    # request['pspReference'] = pspReference
    request['merchantAccount'] = merchant_account
    request['amount'] = {
        'value': int(modAmount),
        'currency': currency
    }
    request['reference'] = modReference

    print("\nThe Mod Request: ")
    print(request)


    if modType == "refund":
        url = "https://checkout-test.adyen.com/v69/payments/"+pspRef+"/refunds"
        response = requests.post(url, headers=headers, json=request)
    if modType == 'cancel':
        url = "https://checkout-test.adyen.com/v69/payments/"+pspRef+"/cancels"
        response = requests.post(url, headers=headers, json=request)
    if modType == 'capture':
        url = "https://checkout-test.adyen.com/v69/payments/"+pspRef+"/captures"
        response = requests.post(url, headers=headers, json=request)
    if modType == 'reversal':
        url = "https://checkout-test.adyen.com/v69/payments/"+pspRef+"/reversals"
        response = requests.post(url, headers=headers, json=request)
    
    modResponse = response.json()

    print("\nThe Modification Response")
    print(modResponse)
    print()
    return (modResponse)







