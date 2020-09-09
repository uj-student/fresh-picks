from flask import render_template, request, redirect, session, url_for, flash, Blueprint
from flask_login import login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from freshpicks import FreshPicksUtilities, db
from freshpicks.databaseModels import Customers, Orders, Products

customers = Blueprint('customers', __name__)


@customers.route('/login', methods=['GET', "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        req = request.form

        customer = Customers.query.filter_by(phone_number=req['phone-number']).first()
        if not customer:
            flash("Account could not be found. Have you registered?", "alert-warning")
            return redirect(url_for('customers.login'))
        else:
            if not customer.password:
                flash("Please set a new password.", "alert-warning")
                return redirect(url_for('.customer_password_reset'))
            if not check_password_hash(customer.password, req['enter-password']):
                flash("Incorrect Password", "alert-danger")
                return redirect(url_for('customers.login'))

        login_user(customer)
        previous_page = request.args.get('next')
        return redirect(previous_page) if previous_page else redirect(url_for('main.products'))

    return render_template('login.html')


@customers.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        req = request.form

        if req['password'] != req['confirm-password']:
            feedback = "Password must be the same. Please try again."
            return render_template('sign-up.html', feedback=feedback)

        customer = Customers(
            fullname=req['full-name'],
            address=req['home-address'],
            town=req['town-city'],
            country=req['state-country'],
            phone_number=str(req['phone-number']).replace(" ", ""),
            email_address=req['email-address'] if req['email-address'] else None,
            gender=req['gender'],
            dob=req['dob'],
            password=generate_password_hash(req['password']),
            terms_and_conditions=True
        )

        existing_phone_number = Customers.query.filter_by(
            phone_number=str(req['phone-number']).replace(" ", "")).first()
        if existing_phone_number:
            flash("Phone number already registered!", "alert-danger")
            return redirect(url_for('customers.signup'))
        if req['email-address']:
            existing_email_address = Customers.query.filter_by(
                phone_number=str(req['email-address']).replace(" ", "")).first()
            if existing_email_address:
                flash("Email already registered!", "alert-danger")
                return redirect(url_for('customers.signup'))

        try:
            db.session.add(customer)
            db.session.commit()
        except Exception:
            flash("Could not create account. Please try later, or call us.", "alert-danger")
            return redirect(url_for('customers.signup'))

        flash(f"Hi {customer.fullname}, thanks for signing up. Please login in to start shopping. Enjoy!",
              "alert-success")
        return redirect(url_for('customers.login'))
    return render_template('sign-up.html')


# @app.route('/checkout')
# def checkout():
#     return render_template('checkout.html')


@customers.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    recent_order = get_my_orders()[0] if get_my_orders() else []

    if request.method == "POST":
        req = request.form
        phone = req['phone-number']
        email = req['email-address']

        user_profile = Customers.query.filter_by(id=current_user.id).first()

        if phone != current_user.phone_number:
            check_for_number = Customers.query.filter_by(phone_number=current_user.phone_number).first()
            if not check_for_number:
                user_profile.phone_number = phone
            else:
                flash("Phone Number already in use.", "alert-info")
                return redirect(url_for('customers.account'))

        if email and email != current_user.email_address:
            check_for_email = Customers.query.filter_by(email_address=current_user.email_address).first()
            if not check_for_email:
                user_profile.email_address = email
            else:
                flash("Email address already in use.", "alert-info")
                return redirect(url_for('customers.account'))

        if req['full-name'] != current_user.fullname:
            user_profile.fullname = req['full-name']
        if req['home-address'] != current_user.address:
            user_profile.address = req['home-address']
        if req['town-city'] != current_user.town:
            user_profile.town = req['town-city']
        if req['gender'] != current_user.gender:
            user_profile.gender = req['gender']
        if req['dob'] != current_user.dob:
            user_profile.dob = req['dob']

        try:
            db.session.commit()
        except Exception:
            flash("Could not update details. Please try again later, or call us", "alert-warning")

        flash("Details updated successfully", "alert-info")
        return redirect(url_for('customers.account'))
    return render_template('account.html', recent_order = recent_order)


@customers.route('/account/order_history')
@login_required
def order_history():
    my_order_history = get_my_orders()
    return render_template('customer/view_order_history.html', order_history = my_order_history)


def get_my_orders():
    return Orders.query.with_entities(
            Orders.customer_order,
            Orders.total_price,
            Orders.delivery_address,
            Orders.status,
            Orders.date_ordered,
            Orders.date_cancelled,
            Orders.date_completed
        ).filter_by(customer_id=current_user.id).order_by(Orders.date_ordered.desc()).all()

@customers.route('/cart')
@login_required
def cart():
    return render_template('cart.html')


@customers.route('/add', methods=['POST'])
@login_required
def add_product_to_cart():
    if request.method == 'POST':
        total_quantity = 0
        total_price = 0
        req = request.form
        name = req['p-name']
        cost_price = Products.query.filter_by(name=name).first().cost_price
        print(f"cost_price: {cost_price}")
        sell_price = req['sell_price']
        image = req['p-image']
        session.modified = True

        quantity = req['quantity'] if 'quantity' in req else 1

        item_array = {
            name: [float(cost_price), float(sell_price), int(quantity), image]
        }

        if 'my_cart' not in session:
            session['my_cart'] = item_array
            session['total_quantity'] = 0
        else:
            t_quantity = 0
            if name in session['my_cart']:
                for k, v in session['my_cart'].items():
                    if k == name:
                        t_quantity = v[2] + int(quantity)
                item_array = {
                    name: [float(cost_price), float(sell_price), int(t_quantity), image]
                }
                session['my_cart'] = array_merge(session['my_cart'], item_array)
            else:
                session['my_cart'] = array_merge(session['my_cart'], item_array)
                total_quantity += t_quantity

        for k, v in session['my_cart'].items():
            total_quantity += v[2]
            total_price += (v[1] * v[2])

        session['total_quantity'] = total_quantity
        session['total_price'] = total_price
    return redirect(url_for('main.products'))


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


@customers.route('/remove/<string:name>')
@login_required
def remove_product_from_cart(name):
    total_price = 0
    total_quantity = 0

    for item in session.get('my_cart').items():
        if item[0] == name:
            session['my_cart'].pop(item[0], None)
            if 'my_cart' in session:
                for k, v in session['my_cart'].items():
                    quantity = int(v[1])
                    sell_price = float(v[0])
                    total_quantity += quantity
                    total_price += sell_price
            break

    if total_quantity < 1:
        clear_cart()
    else:
        session['total_quantity'] = total_quantity
        session['total_price'] = total_price

    return redirect(url_for('customers.cart'))


def clear_cart():
    session.pop('my_cart')
    session['total_quantity'] = ""
    session['total_price'] = 0


# @app.route('/wish')
# def wish():
#     return render_template('wishlist.html')


@customers.route('/place_order', methods=['POST'])
@login_required
def process_order():
    if request.method == "POST":
        req = request.form
        if 'my_cart' in session:
            customer_order = ""
            cost_order = ""
            for k, v in session['my_cart'].items():
                customer_order += f"{k} @ {FreshPicksUtilities.formatToCurrency(v[1])} x {v[2]}\n"
                cost_order += f"{k} @ {FreshPicksUtilities.formatToCurrency(v[0])} x {v[2]}\n"

            order_address = f"{req['delivery-address']}, {req['town']}" if req[
                'delivery-address'] else current_user.address

            my_order = Orders(customer_id=current_user.id,
                              customer_order=customer_order,
                              cost_order=cost_order,
                              total_price=session['total_price'],
                              delivery_address=order_address,
                              additional_instructions=req['instructions'])

            db.session.add(my_order)
            db.session.commit()
            flash("Your order has been received.")
            clear_cart()
    return render_template('cart.html')


@customers.route('/reset_password', methods=['POST', 'GET'])
def customer_password_reset():
    if request.method == 'POST':
        req = request.form
        entered_number = req['phone-number']
        new_password = req['new-password']
        confirm_password = req['confirm-password']

        user_profile = Customers.query.filter_by(phone_number=entered_number).first()
        password = ""

        if user_profile and not user_profile.password:
            if len(new_password) > 9 and new_password == confirm_password:
                user_profile.password = generate_password_hash(new_password)
                try:
                    db.session.commit()
                except Exception as error:
                    pass
            else:
                flash("Passwords must be at least 10 characters and match. Please choose a strong password.",
                      "alert-danger")
                return redirect(url_for(".customer_password_reset"))
        else:
            flash("Cannot reset password at the moment. Please contact us for help.", "alert-danger")
            return redirect(url_for(".customer_password_reset"))

        flash("Your password has been successfully reset. Use new password to log in", "alert-info")
        return redirect(url_for(".login"))

    return render_template('password_reset.html')
