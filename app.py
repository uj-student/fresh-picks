import functools
import traceback

from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

import Utils
import Utils as util
import databaseManager as db
from FreshPicksObjects import User

# from flask_login import login_user

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
    product_list = db.get_products()
    basket_list, extra_list = util.convert_to_Product(product_list)
    return render_template('products.html', baskets=basket_list, extras=extra_list)


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
            session.clear()
            session['user_id'] = user_profile.get_user_id()
            return redirect(url_for('product'))

    return render_template('login.html', feedback=error)


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
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

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view


@app.route('/wish')
def wish():
    session.clear()
    return render_template('wishlist.html')

if __name__ == '__main__':
    app.run(debug=True)
