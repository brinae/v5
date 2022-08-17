# Adyen Demo: 
/paymentMethods, /payments, /paymentDetails with 3DS2 (Challenge Requested, one-off transactions)
  
## How to run ##
1. Download some .jpg or .png files of pretend items you want to sell. 
2. Add those to the app/static/uploads folder
3. Create you .env file as per the [example here.](https://github.com/adyen-examples/adyen-python-online-payments#installation)
4. Open terminal and `cd` to the repo folder
5. Run `source ./setup.sh` 
  - This will create a database file, database.db, which will store all of your users, products, cart items, and payment methods
  - This will also install flask, sqlite3, and the Adyen SDKs
6. Run `./start.sh`
7. Open a private browser tab and go to `http://localhost:8080/add`
8. Add your first item, choose the image from the uploads folder from step 2. Designate the price, name, description, etc. 
9. Revisit the URL from step 7 for each item you want to add. I think it's most fun to have at least two. 
10. Go to the home page: http://localhost:8080/
11. Click `Sign In`
   - Click register, and create a user. I recommend creating a user for a specific country or region, for example:
      - US Test, us@test.com, currency: USD
      - Emails do not have to be valid. Passwords do have to match. [Currency must be ISO code](https://en.wikipedia.org/wiki/ISO_4217).
12. Return to the home page and sign in. You can now click on an item and add it to your cart. 
13. From the cart page, you can choose Drop-In or a specific component. Both will use the /paymentMethods endpoint to identify the available payment methods based on your user (currency) and what's enabled in your CA. 

## Notes ##
- I'm not a front-end developer, so it's not pretty.

- I'm also not a back-end developer so it's rough, as in it was written for my understanding to follow items through the program rather than simplicity. 
=======

