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

	print(" ")
	print("Transaction Variant-> Payment Type: " + txvariant)
	print(" ")
	order_ref = str(uuid.uuid4())

	payments_request = {
	'amount': {
		'value': amount,
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
	'recurringProcessingModel': "CardOnFile",
	'shopperInteraction': "Ecommerce", 
	'authenticationData': {
		'attemptAuthentication': 'always'
	},
	'threeDS2RequestData': {
		'deviceChannel': 'app',
		'threeDSRequestorChallengeInd': "03"
	}
	}
	payments_request.update(payment_info)
	

	print("\npayments request:\n%s"  %(payments_request))

	payments_response = adyen.checkout.payments(payments_request)
	formatted_response = json.dumps((json.loads(payments_response.raw_response)))

	print("\n/payments response:\n%s"  %(formatted_response))
	return formatted_response




    # request = {}

    # request['amount'] = {"value": amount*100, "currency": currency}
    # request['shopperEmail'] = email
    # request['reference'] = reference
    # request['storePaymentMethod'] = True
    # request['shopperInteraction'] = 'Ecommerce'
    # request['recurringProcessingModel'] = "cardOnFile"
    # # set redirect URL required for some payment methods
    # request['returnUrl'] = f"{host_url}/redirect?shopperOrder=myRef"
    # request['shopperReference'] = shopperReference
    # request['shopperName'] = {
    #                             "firstName": firstName,
    #                             "lastName": lastName
    #                          }
    # request['billingAddress'] = {
    #                                 "city": city, 
    #                                 "country": country, 
    #                                 "houseNumberOrName": houseNumber, 
    #                                 "postalCode": zipcode, 
    #                                 "street": street
    #                             }
    # print(method)
    # request['paymentMethod'] = method
    # print(request)
    # # print(request.paymentMethod)
    # # '''
    # # FOR KLARNA (ON HOLD) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # # request['lineItems'] = [
    # #     {
    # #         "quantity": "1",
    # #         "taxPercentage": "0",
    # #         "description": "amsterdam print",
    # #         "id": "amsterdamPrint",
    # #         "amountIncludingTax": "500",
    # #         "productUrl": "URL_TO_PURCHASED_ITEM",
    # #         "imageUrl": "URL_TO_PICTURE_OF_PURCHASED_ITEM"
    # #     },
    # #     {
    # #         "quantity": "1",
    # #         "taxPercentage": "0",
    # #         "description": "toronto print",
    # #         "id": "torontoPrint",
    # #         "amountIncludingTax": "500",
    # #         "productUrl": "URL_TO_PURCHASED_ITEM",
    # #         "imageUrl": "URL_TO_PICTURE_OF_PURCHASED_ITEM"
    # #     }
    # # ]
    # # '''
    # request['countryCode'] = country
    # result = adyen.checkout.payments(request)
    # print(request)
    # print(result)
    # formatted_response = json.dumps((json.loads(result.raw_response)))
    # print(formatted_response)	
    # return formatted_response


# def choose_currency(payment_method):
# 	if payment_method == "alipay":
# 		return "CNY"
# 	elif payment_method == "dotpay":
# 		return "PLN"
# 	elif payment_method == "boletobancario":
# 		return "BRL"
# 	elif payment_method == "ach" or payment_method == "paypal":
# 		return "USD"
# 	else:
# 		return "EUR"
