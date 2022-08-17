import main.config as config
import Adyen
import json
from main.config import *


def get_payment_details(frontend_request):
    adyen = Adyen.Adyen()
    adyen.payment.client.platform = "test"
    adyen.client.xapikey = get_adyen_api_key()

    details_request = frontend_request.get_json()

    print("\n/payments/details request:\n" + str(details_request))

    details_response = adyen.checkout.payments_details(details_request)
    formatted_response = json.loads(details_response.raw_response)

    print("\npayments/details response:\n" + str(formatted_response))
    return formatted_response
