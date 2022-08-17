const clientKey = JSON.parse(document.getElementById('client-key').innerHTML);
const type = JSON.parse(document.getElementById('integration-type').innerHTML);
const chosenPM = type;

async function startCheckout() {
	console.log("!!!!!!!!", type)
	console.log("\nCheckout Started.")
    try {
        const checkout = await createAdyenCheckout()
		console.log("\n stored methods: ", checkout.paymentMethodsResponse.storedPaymentMethods)
        console.log('\nCheckout Object (Configuration):\n', checkout)
		console.log("\nMounting Component.")
		if (isNaN(type)){
			const component = checkout.create(type).mount("#component");

		}
		else {
			const storedPaymentMethod = checkout.paymentMethodsResponse.storedPaymentMethods[chosenPM];
			const card = checkout.create("card", storedPaymentMethod).mount("#component");

		}
	} catch (error) {
		console.error(error);
		alert("Error occurred. Look at console for details");
	}
}

// Start the Checkout workflow
async function createAdyenCheckout() {
	console.log("\nCreating Configuration Object.")
    const paymentMethodsResponse = await callServer("/api/getPaymentMethods");
    const configuration = {
        paymentMethodsResponse,
        clientKey,
        locale: "en_US",
        environment: "test",
        showPayButton: true,
        paymentMethodsConfiguration: {
            ideal: {
                showImage: true
            },
            card: {
                hasHolderName: true,
                holderNameRequired: true,
                //billingAddressRequired: false,
                name: "Credit or Debit card",
                enableStoreDetails: true,
				billingAddressRequired: false,
                brands: ['mc', 'visa', 'amex', 'bcmc', 'cartebancaire', 'diners', 'discover', 'jcb', 'maestro'],
                storedCard: {
                    //hideCVC: true,
                }
            },
            paypal: {
                environment: "test", // Change this to "live" when you're ready to accept live PayPal payments
                countryCode: "US", // Only needed for test. This will be automatically retrieved when you are in production.
                intent: "authorize" // Change this to "authorize" if the payments should not be captured immediately. Contact Support to enable this flow.
            }
        },
        onSubmit: (state, component) => {
			console.log("\nPayment info submitted")
            console.log(state);

            if (state.isValid) {
				console.log("\n Handling submission, and reaching out to server to initiate payment.")
                handleSubmission(state, component, "/api/initiatePayment");
            }
        },
        onAdditionalDetails: (state, component) => {
			console.log("\n Handling additional details, and reaching out to server to make /payment/details request.")
            handleSubmission(state, component, "/api/submitAdditionalDetails");
        }
    };
    console.log("\nConfiguration: \n", configuration)
    return new AdyenCheckout(configuration);
}


// Calls your server endpoints
async function callServer(url, data) {
	const res = await fetch(url, {
		method: "POST",
		body: data ? JSON.stringify(data) : "",
		headers: {
			"Content-Type": "application/json"
		}
	});

	return await res.json();
}

// Event handlers called when the shopper selects the pay button,
// or when additional information is required to complete the payment
async function handleSubmission(state, component, url) {
	try {
		const res = await callServer(url, state.data);
        console.log(res)
		handleServerResponse(res, component);
	} catch (error) {
		console.error(error);
		alert("Error occurred. Look at console for details");
	}
}

// Handles responses sent from your server to the client
function handleServerResponse(res, component) {
    console.log("RES: ", component)
	if (res.action) {
		component.handleAction(res.action);
	} else {
		switch (res.resultCode) {
			case "Authorised":
				window.location.href = "/result/success";
				break;
			case "Pending":
			case "Received":
				window.location.href = "/result/pending";
				break;
			case "Refused":
				window.location.href = "/result/failed";
                console.log('Result:', res)
				break;
			default:
                console.log('Result:', res)
				window.location.href = "/result/error";
				break;
		}
	}
}

function filterUnimplemented(pm) {
	pm.paymentMethods = pm.paymentMethods.filter((it) =>
		[
			"scheme",
            "dropin",
			"ideal",
			"dotpay",
			"giropay",
			"sepadirectdebit",
			"directEbanking",
			"ach",
			"alipay",
			"klarna_paynow",
			"klarna",
			"klarna_account",
			"paypal",
			"boletobancario_santander",
			"storedPaymentMethods"
		].includes(it.type)
	);
	return pm;
}

startCheckout();