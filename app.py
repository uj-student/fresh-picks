import os
import time
import traceback

from PIL import Image
from flask import Flask, g, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

import FreshPicksUtilities
import FreshPicksUtilities as util
import databaseManager as db
from FreshPicksObjects import User, UserUpdatedDetails, Orders, ProductObject, AdminUser

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


# @app.route('/shop')
# def shop():
#     return render_template('shop.html')


@app.route('/cart')
def cart():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('cart.html')


@app.route('/products')
def products():
    product_list = db.get_products()
    basket_list, extra_list = util.convert_db_result_to_product(product_list)
    basket_display_list = []
    for basket in basket_list:
        if basket.get_is_display() == 1:
            basket_display_list.append(basket)
    extras_display_list = []
    for extra in extra_list:
        if extra.get_is_display() == 1:
            extras_display_list.append(extra)
    return render_template('products.html', baskets=basket_display_list, extras=extras_display_list)


@app.before_request
def before_request():
    g.user = None
    g.admin = None

    if 'user_name' in session:
        g.user = session['user_name']
    elif 'admin_username' in session:
        g.admin = session['admin_username']


def is_customer_logged_in():
    if not g.user:
        return redirect(url_for('login'))

def is_admin_logged_in():
    if not g.admin:
        return redirect(url_for('admin'))


@app.route('/login', methods=['GET', "POST"])
def login():
    error = ""
    if request.method == 'POST':
        req = request.form

        user_profile = db.get_user_profile(req['phone-number'])
        if user_profile is None:
            error = "Account could not be found. Have you registered?"
        else:
            user_profile = FreshPicksUtilities.convert_db_result_to_user(user_profile)
            if not check_password_hash(user_profile.get_user_password(), req['enter-password']):
                error = "Incorrect Password"

        if not error:
            setupUserSession(user_profile)
            return redirect(url_for('products'))

    return render_template('login.html', feedback=error)


@app.route('/admin', methods=['GET', "POST"])
def admin():
    error = ""
    if g.admin:
        return redirect(url_for('admin_view', view='all_orders'))
    if request.method == 'POST':
        req = request.form

        user_profile = db.get_admin_account(req['user-name'])
        if user_profile is None:
            flash("Account could not be found. Please contact Admin.", "alert-danger")
            return render_template('/admin/admin_login.html')
        else:
            user_session = FreshPicksUtilities.convert_db_result_to_admin(user_profile)
            if not check_password_hash(user_profile[2], req['enter-password']):
                flash("Incorrect Password", "alert-danger")
                return render_template('/admin/admin_login.html')

        if not error:
            setupAdminSession(user_session)
            return redirect(url_for('admin_view', view='all_orders'))
    return render_template('/admin/admin_login.html')


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


def setupAdminSession(adminUser):
    session.clear()
    session['admin_username'] = adminUser.get_username()
    session['name'] = adminUser.get_name()


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
            fullname=req['full-name'],
            address=req['home-address'],
            town=req['town-city'],
            country=req['state-country'],
            phone_number=str(req['phone-number']).replace(" ", ""),
            gender=req['gender'],
            dob=req['dob'],
            password=generate_password_hash(req['password']),
            terms_and_conditions=1,
            email_address=req['email-address']
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


# @app.route('/checkout')
# def checkout():
#     return render_template('checkout.html')


@app.route('/logout')
def logout():
    goto =""
    if g.user:
        goto = "home"
    elif g.admin:
        goto = "admin"
    session.clear()
    return redirect(url_for(goto))


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
            user_profile = FreshPicksUtilities.convert_db_result_to_user(user_profile)
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
    if not g.user:
        flash('Please Login to shop.', "alert-warning")
        return redirect(url_for('login'))
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


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


@app.route('/remove/<string:name>')
def remove_product_from_cart(name):
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


# @app.route('/wish')
# def wish():
#     return render_template('wishlist.html')


@app.route('/order', methods=['POST'])
def process_order():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == "POST":
        req = request.form
        if 'my_cart' in session:
            content = ""
            for k, v in session['my_cart'].items():
                content += f"{k} @ {FreshPicksUtilities.formatToCurrency(v[0])} x {v[1]}\n"
            order_address = f"{req['delivery-address']}, {req['town']}" if req['delivery-address'] else session[
                'user_address']

            order_request = Orders(customer_id=session['user_id'], contents=content, total_price=session['total_price'],
                                   delivery_address=order_address, instructions=req['instructions'])
            db.create_order(order_request)
            print(f"Contents: {content}\n{order_address}")
            flash("Your order has been received.")
            clear_cart()
    return render_template('cart.html')


# an idea
my_views = {
    "pending": "pending_orders",
    "complete": "completed_orders",
    "cancel": "cancelled_orders",
    "all": "all_orders"
}


@app.route('/admin/<path:view>')
def admin_view(view):
    if not g.admin:
        return redirect(url_for('admin'))
    orders_list = []
    orders = ""
    if "orders" in view:
        if view == "pending_orders":
            orders = db.get_orders_by_status("pending")
        elif view == "completed_orders":
            orders = db.get_orders_by_status("complete")
        elif view == "cancelled_orders":
            orders = db.get_orders_by_status("cancel")
        elif view == "all_orders":
            orders = db.get_all_orders()
        for order in orders:
            orders_list.append(
                Orders(customer_id=order[1], contents=order[2], total_price=order[3], delivery_address=order[4],
                       status=order[5], date_created=order[6], order_id=order[0]))
        return render_template('admin/manage_orders.html', orders_list=orders_list)
    elif view == "customers":
        user_list = db.get_all_customers()
        customer_list = []
        for customer in user_list:
            customer_list.append(FreshPicksUtilities.convert_db_result_to_user(customer))
        return render_template('admin/manage_customers.html', customer_list=customer_list)
    elif view == "admin_users":
        user_list = db.get_all_admins()
        admin_list = []
        for user in user_list:
            admin_list.append(FreshPicksUtilities.convert_db_result_to_admin(user))
        return render_template('admin/manage_users.html', admin_list=admin_list)
    elif view == "products":
        product_list = db.get_products()
        basket_list, extra_list = util.convert_db_result_to_product(product_list)
        basket_list = array_merge(basket_list, extra_list)
        return render_template('admin/manage_products.html', basket_list=basket_list)
    return render_template('admin/manage_products.html', basket_list=[])


@app.route('/mark_complete', methods=['POST'])
def mark_complete():
    if not g.admin:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        new_status = request.form['_order_status']
        current_status = request.form['_current_status']
        order_id = request.form['_order_id']
        db.update_order_status(new_status=new_status, old_status=current_status, order_id=order_id)
    return redirect(url_for('admin_view', view="pending_orders"))


@app.route('/admin/remove/<int:product_id>/<int:display>')
def toggle_product_display(product_id, display):
    if not g.admin:
        return redirect(url_for('admin'))
    display = 1 - display
    db.change_product_display(display=display, product_id=product_id)
    return redirect((url_for('admin_view', view="products")))


@app.route('/admin/products/add', methods=['POST', 'GET'])
def add_product():
    if not g.admin:
        return redirect(url_for('admin'))
    if request.method == "POST":
        req = request.form
        image_location = upload_picture(request.files['display-image'])
        new_product = ProductObject(
            name=req['product-name'],
            description=req['product-description'],
            price=req['price'],
            image="/" + image_location,
            is_main=0 if req['type'] == "extra" else 1,
            is_display=1 if req['display'] == "yes" else 0
        )
        db.add_product(new_product)
        return redirect(url_for('add_product'))
    return render_template('admin/add_products.html')


@app.route('/admin/users/add', methods=['POST', 'GET'])
def add_admin_user():
    if not g.admin:
        return redirect(url_for('admin'))
    if request.method == "POST":
        req = request.form

        if len(req['username']) < 6:
            flash("Username must be at least 6 characters long. Please try again.", "alert-warning")
            # return redirect(url_for("add_admin_user"))
            return render_template('admin/admin_register.html')

        if len(req['password']) < 10:
            flash("Password must be at least 10 characters. Please choose a strong password.", "alert-danger")
            # return render_template('admin/admin_register.html')
            return redirect(url_for("add_admin_user"))

        if req['password'] != req['confirm-password']:
            flash("Ensure that passwords are the same. Please try again.", "alert-danger")
            return render_template('admin/admin_register.html')

        if len(req['phone-number']) < 7:
            flash("Phone number may be short a few digits", "alert-warning")

        admin_account = AdminUser(
            name=req['fullname'],
            email=req['email-address'],
            cellphone=str(req['phone-number']).replace(" ", ""),
            password=generate_password_hash(req['password']),
            username=req['username'],
            date_created=0
        )

        try:
            db.add_admin_user(admin_account)
        except Exception as error:
            flash(f"Could not create account. \nReason: {error}", "alert-danger")
            traceback.print_exc()
            return redirect(url_for("add_admin_user"))

        flash(f"{admin_account.get_username()}'s account has been created successfully!", "alert-success")

        return redirect(url_for("add_admin_user"))
    return render_template('admin/admin_register.html')


def upload_picture(uploaded_picture):
    f_name, f_ext = os.path.splitext(uploaded_picture.filename)
    image_name = f_name + str(round(time.time())) + f_ext
    # image_path = os.path.join(app.root_path, 'static/images', image_name)
    image_path = 'static/images/' + image_name
    resize = (300, 300)
    resize_image = Image.open(uploaded_picture)
    resize_image.thumbnail(resize)
    resize_image.save(image_path)
    return image_path


@app.route('/reset_password', methods=['POST', 'GET'])
def customer_password_reset():
    if request.method == 'POST':
        req = request.form
        phone_number = req['phone-number']
        new_password = req['new-password']
        confirm_password = req['confirm-password']
        user_profile = db.get_user_profile(phone_number)
        password = ""

        if user_profile and not user_profile[9]:
            if len(new_password) > 9 and new_password == confirm_password:
                password = generate_password_hash(new_password)
            else:
                flash("Passwords must be at least 10 characters and match. Please choose a strong password.", "alert-danger")
                return redirect(url_for("customer_password_reset"))
        else:
            flash("Cannot reset password at the moment. Please contact us for help.", "alert-danger")
            return redirect(url_for("customer_password_reset"))
        return redirect(url_for("customer_password_reset"))

    return  render_template('password_reset.html')

if __name__ == '__main__':
    app.run(debug=True)
