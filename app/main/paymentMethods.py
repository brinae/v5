import Adyen
from main.config import get_adyen_api_key, get_adyen_merchant_account
import json
import sqlite3, hashlib, os
from Adyen.util import is_valid_hmac_notification
from flask import Flask, render_template, send_from_directory, request, abort, session, url_for, redirect

def getPaymentMethods(amount, reference, country, currency, shopperReference):

    adyen = Adyen.Adyen()
    adyen.payment.client.xapikey = get_adyen_api_key()
    adyen.payment.client.platform = "test" # change to live for production
    adyen.payment.client.merchant_account = get_adyen_merchant_account()

    request = {}

    request['merchantAccount'] = adyen.payment.client.merchant_account
    request['amount'] = {"value": amount*100, "currency": currency}
    request['reference'] = reference  # provide your unique payment reference
    request['countryCode'] = country
    request['shopperReference'] = shopperReference

    result = adyen.checkout.payment_methods(request)
    print(result)
    print(type(result))
    formatted_response = json.dumps((json.loads(result.raw_response)), sort_keys=True, indent=4)
    print("/paymentMethods response:\n" + formatted_response)
    print(type(formatted_response))

    paymentMethods = json.loads(formatted_response)
    print(paymentMethods)
    print(type(paymentMethods))
    pM = paymentMethods['paymentMethods']
    pMTypelist = [d['type'] for d in pM]
    pMNamelist = [d['name'] for d in pM]
    res = {}
    for key in pMNamelist:
        for value in pMTypelist:
            res[key] = value
            pMTypelist.remove(value)
            break  

    return res