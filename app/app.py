import logging
import sqlite3, hashlib, os
from Adyen.util import is_valid_hmac_notification
from flask import Flask, render_template, send_from_directory, request, abort, session, url_for, redirect

from main.payments import *
from main.redirect import *
from main.additional_details import *
from main.config import *
from main.paymentMethods import *
from main.paymentMethods2 import *
from werkzeug.utils import secure_filename

import json
import string
import random


reference = (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))


def create_app():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    app = Flask('app')
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

    # Register 404 handler
    app.register_error_handler(404, page_not_found)

    def getLoginDetails():
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            if 'email' not in session:
                loggedIn = False
                firstName = ''
                noOfItems = 0
            else:
                loggedIn = True
                cur.execute("SELECT userId, firstName FROM users WHERE email = ?", (session['email'], ))
                userId, firstName = cur.fetchone()
                cur.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
                noOfItems = cur.fetchone()[0]
        conn.close()
        return (loggedIn, firstName, noOfItems)


    ## Routes: ##

    # Home page
    @app.route("/")
    def root():
        loggedIn, firstName, noOfItems = getLoginDetails()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image FROM products')
            itemData = cur.fetchall()
        itemData = parse(itemData)   
        return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

    # UI to add product to the items table
    @app.route("/add")
    def admin():
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
        conn.close()
        return render_template('add.html')

    # Adds product to the items table in database.db
    @app.route("/addItem", methods=["GET", "POST"])
    def addItem():
        if request.method == "POST":
            name = request.form['name']
            price = float(request.form['price'])
            description = request.form['description']

            #Uploading image procedure
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagename = filename
            with sqlite3.connect('database.db') as conn:
                try:
                    cur = conn.cursor()
                    cur.execute('''INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)''', (name, price, description, imagename))
                    conn.commit()
                    msg="added successfully"
                except:
                    msg="error occured"
                    conn.rollback()
            conn.close()
            print(msg)
            return redirect('/')

    # UI to remove item from items table
    @app.route("/remove")
    def remove():
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
            data = cur.fetchall()
        conn.close()
        return render_template('remove.html', data=data)

    # Removes item from items table
    @app.route("/removeItem")
    def removeItem():
        productId = request.args.get('productId')
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
                conn.commit()
                msg = "Deleted successsfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for('root'))

    # To view user profile. Following functions allow edits to profile. 
    @app.route("/account/profile")
    def profileHome():
        if 'email' not in session:
            return redirect(url_for('root'))
        loggedIn, firstName, noOfItems = getLoginDetails()
        return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

    @app.route("/account/profile/edit")
    def editProfile():
        if 'email' not in session:
            return redirect(url_for('root'))
        loggedIn, firstName, noOfItems = getLoginDetails()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, email, firstName, lastName, houseNumber, street, address2, zipcode, city, state, country, phone, currency FROM users WHERE email = ?", (session['email'], ))
            profileData = cur.fetchone()
        conn.close()
        return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

    @app.route("/account/profile/changePassword", methods=["GET", "POST"])
    def changePassword():
        if 'email' not in session:
            return redirect(url_for('loginForm'))
        if request.method == "POST":
            oldPassword = request.form['oldpassword']
            oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
            newPassword = request.form['newpassword']
            newPassword = hashlib.md5(newPassword.encode()).hexdigest()
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'], ))
                userId, password = cur.fetchone()
                if (password == oldPassword):
                    try:
                        cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                        conn.commit()
                        msg="Changed successfully"
                    except:
                        conn.rollback()
                        msg = "Failed"
                    return render_template("changePassword.html", msg=msg)
                else:
                    msg = "Wrong password"
            conn.close()
            return render_template("changePassword.html", msg=msg)
        else:
            return render_template("changePassword.html")

    @app.route("/updateProfile", methods=["GET", "POST"])
    def updateProfile():
        if request.method == 'POST':
            email = request.form['email']
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            houseNumber = request.form['houseNumber']
            street = request.form['street']
            address2 = request.form['address2']
            zipcode = request.form['zipcode']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            phone = request.form['phone']
            currency = request.form['currency']
            with sqlite3.connect('database.db') as con:
                    try:
                        cur = con.cursor()
                        cur.execute('UPDATE users SET firstName = ?, lastName = ?, houseNumber = ?, street = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ?, currency = ? WHERE email = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                        con.commit()
                        msg = "Saved Successfully"
                    except:
                        con.rollback()
                        msg = "Error occured"
            con.close()
            return redirect(url_for('editProfile'))

    # UI to log in - also shows rows from users table
    @app.route("/loginForm")
    def loginForm():
        if 'email' in session:
            return redirect(url_for('root'))
        else:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT email, firstName FROM users")
                users = cur.fetchall()
            conn.close()
            return render_template('login.html', userData = users, error='')

    # Logs in a user (starts flask session)
    @app.route("/login", methods = ['POST', 'GET'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            if is_valid(email, password):
                session['email'] = email
                return redirect(url_for('root'))
            else:
                error = 'Invalid UserId / Password'
                return render_template('login.html', error=error)

    # Product description page
    @app.route("/productDescription")
    def productDescription():
        loggedIn, firstName, noOfItems = getLoginDetails()
        productId = request.args.get('productId')
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image FROM products WHERE productId = ?', (productId, ))
            productData = cur.fetchone()
        conn.close()
        return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)

    # Adds an item to the cart table
    @app.route("/addToCart")
    def addToCart():
        if 'email' not in session:
            return redirect(url_for('loginForm'))
        else:
            productId = int(request.args.get('productId'))
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
                userId = cur.fetchone()[0]
                try:
                    cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                    conn.commit()
                    msg = "Added successfully"
                except:
                    conn.rollback()
                    msg = "Error occured"
            conn.close()
            return redirect(url_for('root'))

    # Shows a cart page and loads the payment options
    @app.route("/cart")
    def cart():
        if 'email' not in session:
            return redirect(url_for('loginForm'))
        loggedIn, firstName, noOfItems = getLoginDetails()
        email = session['email']
        print("\nUser %s's Cart!" %(firstName))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT country FROM users WHERE email = ?", (email, ))
            country = cur.fetchone()[0]
            cur.execute("SELECT currency FROM users WHERE email = ?", (email, ))
            currency = cur.fetchone()[0]
            cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
            userId = cur.fetchone()[0]
            cur.execute("SELECT shopperReference FROM users WHERE email = ?", (email, ))
            global shopperReference
            shopperReference = cur.fetchone()[0]
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
            products = cur.fetchall()
        conn.close()
        global totalPrice
        totalPrice = 0
        for row in products:
            totalPrice += row[2]
        availablePaymentMethods = getPaymentMethods(totalPrice, reference, country, currency, shopperReference)
        print("\nAVAILABLE PAYMENT METHODS: %s" %(availablePaymentMethods))
        return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, client_key=get_adyen_client_key(), paymentMethods = availablePaymentMethods)

    # Removes an item from the cart table
    @app.route("/removeFromCart")
    def removeFromCart():
        if 'email' not in session:
            return redirect(url_for('loginForm'))
        email = session['email']
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
            userId = cur.fetchone()[0]
            try:
                cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
                conn.commit()
                msg = "removed successfully"
            except:
                conn.rollback()
                msg = "error occured"
        conn.close()
        return redirect(url_for('root'))

    # Logs out a user (ends flask session)
    @app.route("/logout")
    def logout():
        session.pop('email', None)
        return redirect(url_for('root'))

    # Confirms that the log in info is valid
    def is_valid(email, password):
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute('SELECT email, password FROM users')
        data = cur.fetchall()
        for row in data:
            if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
                return True
        return False

    # Creates a row in the users table based on input. Where #1 Shopper Reference is created. 
    @app.route("/register", methods = ['GET', 'POST'])
    def register():
        if request.method == 'POST':
            #Parse form data    
            password = request.form['password']
            email = request.form['email']
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            houseNumber = request.form['houseNumber']
            street = request.form['street']
            address2 = request.form['address2']
            zipcode = request.form['zipcode']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            phone = request.form['phone']
            currency = request.form['currency']
            shopperReference =  (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))) #1 Create Shopper Reference when account is created
            print("\nShopper Reference %s Created!" %(shopperReference))
            with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('INSERT INTO users (password, email, firstName, lastName, houseNumber, street, address2, zipcode, city, state, country, phone, currency, shopperReference) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, houseNumber, street, address2, zipcode, city, state, country, phone, currency, shopperReference))

                    con.commit()

                    msg = "Registered Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
            con.close()
            return render_template("login.html", error=msg)

    # UI to register
    @app.route("/registerationForm")
    def registrationForm():
        return render_template("register.html")

    # Loads the coomponents needed for checkout - when you click on your payment option from the cart page
    @app.route('/checkout/<integration>')
    def checkout(integration):
        global method
        method = integration
        print("\nIntegration type %s Chosen" %(method))
        print("Loading Component page")
        return render_template('component.html', method=integration, client_key=get_adyen_client_key())

    # Gets the available payment methods based on shopper data
    @app.route('/api/getPaymentMethods', methods=['GET', 'POST'])
    def get_payment_methods():
        if 'email' not in session:
            return redirect(url_for('loginForm'))
        email = session['email']
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT country FROM users WHERE email = ?", (email, ))
            country = cur.fetchone()[0]
            cur.execute("SELECT currency FROM users WHERE email = ?", (email, ))
            currency = cur.fetchone()[0]
            cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
            userId = cur.fetchone()[0]
            cur.execute("SELECT shopperReference FROM users WHERE email = ?", (email, ))
            shopperReference = cur.fetchone()[0]
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
            products = cur.fetchall()
        conn.close()
        global totalPrice
        totalPrice = 0
        for row in products:
            totalPrice += row[2]
        pm = getPaymentMethods2(totalPrice, reference, country, currency, shopperReference)
        return pm

    # Passes info to the /payments request
    @app.route('/api/initiatePayment', methods=['POST'])
    def initiate_payment():
        host_url = request.host_url
        if 'email' not in session:
            return redirect(url_for('loginForm'))
        loggedIn, firstName, noOfItems = getLoginDetails()
        email = session['email']
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            loggedIn = True
            cur.execute("SELECT userId, firstName, lastName, houseNumber, street, address2, zipcode, city, state, country, currency, shopperReference FROM users WHERE email = ?", (session['email'], ))
            record = cur.fetchone()
        conn.close()
        amount = totalPrice
        # email = session['email']
        firstName = record[1]
        lastName = record[2]
        houseNumber = record[3]
        street = record[4]
        address2 = record[5]
        zipcode = record[6]
        city = record[7]
        state = record[8]
        country = record[9]
        currency = record[10]
        shopperReference = record[11]       
        return adyen_payments(request, host_url, email, amount, firstName, lastName, houseNumber, street, address2, zipcode, city, state, country, reference, currency, shopperReference)

    # Gets additonal details from /payment/details request
    @app.route('/api/submitAdditionalDetails', methods=['POST'])
    def payment_details():
        return get_payment_details(request)

    # Redirect logic
    @app.route('/api/handleShopperRedirect', methods=['POST', 'GET'])
    def handle_redirect():
        values = request.values.to_dict()  # Get values from query params in request object
        details_request = {}

        if "payload" in values:
            details_request["details"] = {"payload": values["payload"]}
        elif "redirectResult" in values:
            details_request["details"] = {"redirectResult": values["redirectResult"]}

        redirect_response = handle_shopper_redirect(details_request)

        # Redirect shopper to landing page depending on payment success/failure
        if redirect_response["resultCode"] == 'Authorised':
            return redirect(url_for('checkout_success'))
        elif redirect_response["resultCode"] == 'Received' or redirect_response["resultCode"] == 'Pending':
            return redirect(url_for('checkout_pending'))
        else:
            return redirect(url_for('checkout_failure'))

    # Below are various results:
    @app.route('/result/success', methods=['GET'])
    def checkout_success():
        return render_template('checkout-success.html')

    @app.route('/result/failed', methods=['GET'])
    def checkout_failure():
        return render_template('checkout-failed.html')

    @app.route('/result/pending', methods=['GET'])
    def checkout_pending():
        return render_template('checkout-success.html')

    @app.route('/result/error', methods=['GET'])
    def checkout_error():
        return render_template('error.html')

    # Handle redirect (required for some payment methods)
    @app.route('/redirect', methods=['POST', 'GET'])
    def redirect2():

        return render_template('component.html', method=None, client_key=get_adyen_client_key())

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                    'img/favicon.ico')

    # Process incoming webhook notifications
    # @app.route('/notifications', methods=['POST'])
    # def webhook_notifications():
    #     """
    #     Receives outcome of each payment
    #     :return:
    #     """
    #     notifications = request.json['notificationItems']
    #     print(notifications)
    #     # for notification in notifications:
    #     #     if is_valid_hmac_notification(notification['NotificationRequestItem'], get_adyen_hmac_key()) :
    #     #         print(f"merchantReference: {notification['NotificationRequestItem']['merchantReference']} "
    #     #               f"result? {notification['NotificationRequestItem']['success']}")
    #     #     else:
    #     #         # invalid hmac: do not send [accepted] response
    #     #         raise Exception("Invalid HMAC signature")

    #     # return '[accepted]'
    #     return notifications

    def allowed_file(filename):
        return '.' in filename and \
                filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    # Used to show items on home page
    def parse(data):
        ans = []
        i = 0
        while i < len(data):
            curr = []
            for j in range(7):
                if i >= len(data):
                    break
                curr.append(data[i])
                i += 1
            ans.append(curr)
        return ans


    return app



def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == '__main__':
    web_app = create_app()

    logging.info(f"Running on http://localhost:{get_port()}")
    web_app.run(debug=True, port=get_port(), host='0.0.0.0')
