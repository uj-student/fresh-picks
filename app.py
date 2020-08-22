import traceback

from flask import Flask, g, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

import Utils
import Utils as util
import databaseManager as db
from FreshPicksObjects import User, UserUpdatedDetails, Orders

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/products')
def products():
    # session.clear()
    product_list = db.get_products()
    basket_list, extra_list = util.convert_to_Product(product_list)
    return render_template('products.html', baskets=basket_list, extras=extra_list)


@app.before_request
def before_request():
    g.user = None

    if 'user_name' in session:
        g.user = session['user_name']


@app.route('/login', methods=['GET', "POST"])
def login():
    error = ""
    if request.method == 'POST':
        req = request.form

        user_profile = db.get_user_profile(req['phone-number'])
        if user_profile is None:
            error = "Account could not be found. Have you registered?"
        else:
            user_profile = Utils.convert_to_User(user_profile)
            if not check_password_hash(user_profile.get_user_password(), req['enter-password']):
                error = "Incorrect Password"

        if not error:
            setupUserSession(user_profile)
            return redirect(url_for('products'))

    return render_template('login.html', feedback=error)


def setupUserSession(user_profile):
    session.clear()
    session['user_id'] = user_profile.get_user_id()
    session['user_first_name'] = user_profile.get_user_first_name()
    session['user_name'] = user_profile.get_user_name()
    session['user_address'] = user_profile.get_user_address()
    session['user_town'] = user_profile.get_user_town()
    session['user_phone'] = user_profile.get_user_phone_number()
    session['user_email'] = user_profile.get_user_email_address()
    session['user_gender'] = user_profile.get_user_gender()
    session['user_dob'] = user_profile.get_user_birthday()


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if g.user:
        return redirect(url_for('home'))
    if request.method == 'POST':
        req = request.form

        if req['password'] != req['confirm-password']:
            feedback = f"Password must be the same. Please try again."
            return render_template('sign-up.html', feedback=feedback)
        user_account = User(
            req['full-name'],
            req['home-address'],
            req['town-city'],
            req['state-country'],
            str(req['phone-number']),
            req['gender'],
            req['dob'],
            generate_password_hash(req['password']),
            1,
            req['email-address'],
        )

        try:
            db.add_user(user_account)
        except Exception as error:
            feedback = f"Could not create account. \nReason: {error}"
            traceback.print_exc()
            return render_template('sign-up.html', feedback=feedback)

        feedback = f"Hi {user_account.get_user_name()}, thanks for signing up. Please login in to start shopping. Enjoy!"

        return render_template('login.html', feedback=feedback)
    return render_template('sign-up.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
def account():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == "POST":
        req = request.form
        phone = req['phone-number']
        email = req['email-address']

        current_user = UserUpdatedDetails(session['user_id'], session['user_name'], session['user_address'],
                                          session['user_town'], session['user_phone'], session['user_email'],
                                          session['user_gender'], session['user_dob'])

        new_user = UserUpdatedDetails("#", req['full-name'], req['home-address'], req['town-city'],
                                      req['phone-number'], req['email-address'], req['gender'], req['dob'])

        is_unique = db.is_unique(phone, email)
        if session['user_phone'] == phone and session['user_email'] == email and (
                req['full-name'] != session['user_name']
                or req['home-address'] != session['user_address']
                or req['town-city'] != session['user_town']
                or req['gender'] != session['user_gender']
                or req['dob'] != session['user_dob']):
            db.update_user(old_data=current_user, new_data=new_user)
            flash("Details updated successfully")
            user_profile = db.get_user_by_id(session['user_id'])
            user_profile = Utils.convert_to_User(user_profile)
            setupUserSession(user_profile)
            return redirect(url_for('account'))
        else:
            if is_unique:
                flash("Phone Number or email already in use.", "alert-info")
                return redirect(url_for('account'))
            elif phone != session['user_phone'] or email != session['user_email']:
                db.update_user(old_data=current_user, new_data=new_user)
    return render_template('account.html')


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    if request.method == 'POST':
        total_quantity = 0
        total_price = 0
        req = request.form
        name = req['p-name']
        price = req['p-price']
        image = req['p-image']
        session.modified = True

        quantity = 1
        item_array = {
            name: [float(price), int(quantity), image]
        }

        if 'my_cart' not in session:
            session['my_cart'] = item_array
            session['total_quantity'] = 0
        else:
            t_quantity = 0
            if name in session['my_cart']:
                for k, v in session['my_cart'].items():
                    if k == name:
                        t_quantity = v[1] + 1
                item_array = {
                    name: [float(price), int(t_quantity)]
                }
                session['my_cart'] = array_merge(session['my_cart'], item_array)
            else:
                session['my_cart'] = array_merge(session['my_cart'], item_array)
                total_quantity += t_quantity

        for k, v in session['my_cart'].items():
            total_quantity += v[1]
            total_price += (v[0] * v[1])

        session['total_quantity'] = total_quantity
        session['total_price'] = total_price
    return redirect(url_for('products'))


@app.route('/remove/<string:name>')
def remove_product(name):
    total_price = 0
    total_quantity = 0

    for item in session.get('my_cart').items():
        if item[0] == name:
            session['my_cart'].pop(item[0], None)
            if 'my_cart' in session:
                for k, v in session['my_cart'].items():
                    quantity = int(v[1])
                    price = float(v[0])
                    total_quantity += quantity
                    total_price += price
            break

    if total_quantity < 1:
        clear_cart()
    else:
        session['total_quantity'] = total_quantity
        session['total_price'] = total_price

    return redirect(url_for('cart'))


def clear_cart():
    session.pop('my_cart')
    session['total_quantity'] = ""
    session['total_price'] = 0


@app.route('/wish')
def wish():
    return render_template('wishlist.html')


@app.route('/order', methods=['POST'])
def process_order():
    if request.method == "POST":
        req = request.form
        if 'my_cart' in session:
            content = ""
            for k, v in session['my_cart'].items():
                content += f"{k} @ {v[0]} x {v[1]}\n"
            order_address = f"{req['delivery-address']}, {req['town']}" if req['delivery-address'] else session[
                'user_address']

            order_request = Orders(customer_id=session['user_id'], contents=content, total_price=session['total_price'],
                                   delivery_address=order_address, instructions=req['instructions'])
            db.create_order(order_request)
            print(f"Contents: {content}\n{order_address}")
            flash("Your order has been received.")
            clear_cart()
    return render_template('cart.html')


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


if __name__ == '__main__':
    app.run(debug=True)
