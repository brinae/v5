import logging
import sqlite3, hashlib, os
import Adyen
import json
import uuid
from main.config import *


def adyen_payments(request, host_url, email, amount, firstName, lastName, houseNumber, street, address2, zipcode, city, state, country, reference, currency, shopperReference):
	adyen = Adyen.Adyen()
	adyen.payment.client.xapikey = get_adyen_api_key()
	adyen.payment.client.platform = "test" # change to live for production
	adyen.payment.client.merchant_account = get_adyen_merchant_account()

	payment_info = request.get_json()

	txvariant = payment_info["paymentMethod"]["type"]

    
	print("\nStarting Payment Request")
	order_ref = reference

	payments_request = {

        'amount': {
            'value': amount * 100,
            'currency': currency
        },
        'channel': 'Web',
        'reference': order_ref,
        'shopperReference': shopperReference,
        'returnUrl': "http://localhost:8080/api/handleShopperRedirect?orderRef=" + order_ref,
        'countryCode': country,
        'shopperLocale': "en_US",
        'storePaymentMethod': 'true',
        'merchantAccount': get_adyen_merchant_account(),
        'recurringProcessingModel': "CardOnFile", # One Off transactions
        'shopperInteraction': "Ecommerce", # Customer Present
        'authenticationData': {
            'threeDSRequestData': {
                'nativeThreeDS': 'preferred'
            }
            # 'attemptAuthentication': 'always'  USED FOR REDIRECT METHOD. 
        },
        # 'threeDS2RequestData': {
        #     'deviceChannel': 'app',
        #     'threeDSRequestorChallengeInd': "03"
        # },
        'billingAddress': {
                "city": city, 
                "country": country, 
                "houseNumberOrName": houseNumber, 
                "postalCode": zipcode, 
                "street": street
        }
	}
	payments_request.update(payment_info)
	

	print("\npayments request:\n%s"  %(payments_request))

	payments_response = adyen.checkout.payments(payments_request)
	formatted_response = json.dumps((json.loads(payments_response.raw_response)))

	print("\n/payments response:\n%s"  %(formatted_response))
	return formatted_response


