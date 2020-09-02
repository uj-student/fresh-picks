import os
import time

from PIL import Image
from flask import g, render_template, request, redirect, session, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from freshpicks import FreshPicksUtilities, app, db
from freshpicks.databaseModels import Customers, AdminUsers, Products, Orders, Messages

# db.create_all()
# print("Hello")
lst = Customers.query.all()
print(lst)
print(len(lst))

PER_PAGE_VIEW = 1

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


@app.route('/test')
def shop():
    return render_template('shop.html')


@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')


@app.route('/products')
def products():
    product_list = Products.query.filter_by(is_displayed=True)
    basket_display_list = []
    extras_display_list = []

    for item in product_list:
        if item.is_basket_item:
            basket_display_list.append(item)
        else:
            extras_display_list.append(item)
    return render_template('products.html', baskets=basket_display_list, extras=extras_display_list)


@app.before_request
def before_request():
    g.user = None
    g.admin = None

    if 'admin_username' in session:
        g.admin = session['admin_username']


@app.route('/login', methods=['GET', "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        req = request.form

        customer = Customers.query.filter_by(phone_number=req['phone-number']).first()
        if not customer:
            flash("Account could not be found. Have you registered?", "alert-warning")
            return redirect(url_for('login'))
        else:
            if not check_password_hash(customer.password, req['enter-password']):
                flash("Incorrect Password", "alert-danger")
                return redirect(url_for('login'))

        login_user(customer)
        previous_page = request.args.get('next')

        # setupUserSession(customer)
        # return redirect(url_for('products'))
        return redirect(previous_page) if previous_page else redirect(url_for('account'))

    return render_template('login.html')


@app.route('/admin', methods=['GET', "POST"])
def admin():
    if g.admin:
        return redirect(url_for('admin_view', view='all_orders'))
    if request.method == 'POST':
        req = request.form

        user_profile = AdminUsers.query.filter_by(username=req['user-name']).first()
        if user_profile is None:
            flash("Account could not be found. Please contact Admin.", "alert-danger")
            return render_template('admin/admin_login.html')
        else:
            if not check_password_hash(user_profile.password, req['enter-password']):
                flash("Incorrect Password", "alert-danger")
                return render_template('admin/admin_login.html')

        setupAdminSession(user_profile)
        return redirect(url_for('admin_view', view='all_orders'))
    return render_template('admin/admin_login.html')


def setupUserSession(user_profile):
    session.clear()
    session['user_id'] = user_profile.id
    session['user_first_name'] = user_profile.fullname.split(' ')[0]
    session['user_name'] = user_profile.fullname
    session['user_address'] = user_profile.address
    session['user_town'] = user_profile.town
    session['user_phone'] = user_profile.phone_number
    session['user_email'] = user_profile.email_address
    session['user_gender'] = user_profile.gender
    session['user_dob'] = user_profile.dob


def setupAdminSession(adminUser):
    session.clear()
    session['admin_username'] = adminUser.username
    session['name'] = adminUser.name


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
            return redirect(url_for('signup'))
        if req['email-address']:
            existing_email_address = Customers.query.filter_by(
                phone_number=str(req['email-address']).replace(" ", "")).first()
            if existing_email_address:
                flash("Email already registered!", "alert-danger")
                return redirect(url_for('signup'))

        try:
            db.session.add(customer)
            db.session.commit()
        except Exception:
            flash("Could not create account. Please try later, or call us.", "alert-danger")
            return redirect(url_for('signup'))

        flash(f"Hi {customer.fullname}, thanks for signing up. Please login in to start shopping. Enjoy!",
              "alert-success")

        return redirect(url_for('login'))
    return render_template('sign-up.html')


# @app.route('/checkout')
# def checkout():
#     return render_template('checkout.html')


@app.route('/logout')
def logout():
    goto = ""
    # if g.user:
    #     goto = "home"
    # elif g.admin:
    #     goto = "admin"
    session.clear()
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
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
                return redirect(url_for('account'))

        if email and email != current_user.email_address:
            check_for_email = Customers.query.filter_by(email_address=current_user.email_address).first()
            if not check_for_email:
                user_profile.email_address = email
            else:
                flash("Email address already in use.", "alert-info")
                return redirect(url_for('account'))

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
        user_profile = Customers.query.filter_by(id=current_user.id).first()
        # login_user(user_profile)
        # setupUserSession(user_profile)
        flash("Details updated successfully", "alert-info")
        return redirect(url_for('account'))
    return render_template('account.html')


@app.route('/add', methods=['POST'])
@login_required
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
                    name: [float(price), int(t_quantity), image]
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


@app.route('/place_order', methods=['POST'])
@login_required
def process_order():
    if request.method == "POST":
        req = request.form
        if 'my_cart' in session:
            content = ""
            for k, v in session['my_cart'].items():
                print(f"Order: {v[0]}")
                content += f"{k} @ {FreshPicksUtilities.formatToCurrency(v[0])} x {v[1]}\n"

            order_address = f"{req['delivery-address']}, {req['town']}" if req['delivery-address'] else session[
                'user_address']

            my_order = Orders(customer_id=session['user_id'],
                              order=content,
                              total_price=session['total_price'],
                              delivery_address=order_address,
                              additional_instructions=req['instructions'])

            db.session.add(my_order)
            db.session.commit()
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
    page = request.args.get('page', 1, type=int)

    if "orders" in view:
        orders = "" # need this to handle the filter in the view
        order_type = "all_orders"
        if view == "pending_orders":
            orders = Orders.query.filter_by(status="pending").paginate(per_page=PER_PAGE_VIEW, page=page)
            order_type = "pending_orders"
        if view == "completed_orders":
            orders = Orders.query.filter_by(status="complete").paginate(per_page=PER_PAGE_VIEW, page=page)
            order_type = "completed_orders"
        elif view == "cancelled_orders":
            orders = Orders.query.filter_by(status="cancel").paginate(per_page=PER_PAGE_VIEW, page=page)
            order_type = "cancelled_orders"
        elif view == "all_orders":
            orders = Orders.query.paginate(per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_orders.html', order_type=order_type, orders_list=orders)
    elif view == "customers":
        customer_list = Customers.query.order_by(Customers.fullname.asc()).paginate(per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_customers.html', customer_list=customer_list)
    elif view == "admin_users":
        admin_list = AdminUsers.query.all()
        return render_template('admin/manage_users.html', admin_list=admin_list)
    elif view == "products":
        product_list = Products.query.order_by(Products.is_basket_item.desc(), Products.name.asc()).paginate(per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_products.html', product_list=product_list)
    elif view == "customer_messages":
        messages_list = Messages.query.all()
        return render_template('admin/manage_comments.html', messages_list=messages_list)
    return render_template('admin/manage_products.html', product_list=[])


@app.route('/mark_complete', methods=['POST'])
def mark_complete():
    if not g.admin:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        new_status = request.form['_order_status']
        current_status = request.form['_current_status']
        order_id = request.form['_order_id']

        my_order = Orders.query.filter_by(id=order_id, status=current_status).first()
        try:
            my_order.status = new_status
            db.session.commit()
        except Exception as error:
            pass
    return redirect(url_for('admin_view', view="pending_orders"))


@app.route('/admin/remove/<int:product_id>')
def toggle_product_display(product_id):
    if not g.admin:
        return redirect(url_for('admin'))

    product = Products.query.filter_by(id=product_id).first()
    display_status = product.is_displayed

    if display_status:
        product.is_displayed = False
    else:
        product.is_displayed = True

    db.session.commit()
    return redirect((url_for('admin_view', view="products")))


@app.route('/admin/products/add', methods=['POST', 'GET'])
def add_product():
    if not g.admin:
        return redirect(url_for('admin'))
    if request.method == "POST":
        req = request.form
        image_location = upload_picture(request.files['display-image'])
        new_product = Products(
            name=req['product-name'],
            description=req['product-description'],
            price=req['price'],
            image_location=f"/{image_location}",
            is_basket_item=False if req['type'] == "extra" else True,
            is_displayed=True if req['display'] == "yes" else False
        )
        try:
            db.session.add(new_product)
            db.session.commit()
        except Exception as error:
            flash(f"Could not add product. \nReason: {error}", "alert-danger")
            return redirect(url_for("add_product"))

        flash(f"{new_product.name} added successfully.", "alert-success")
        return redirect(url_for('add_product'))
    return render_template('admin/add_products.html')


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

        admin_account = AdminUsers(
            username=req['username'],
            password=generate_password_hash(req['password']),
            cellphone_number=str(req['phone-number']).replace(" ", ""),
            name=req['fullname'],
            email_address=req['email-address']
        )

        try:
            db.session.add(admin_account)
            db.session.commit()
        except Exception as error:
            flash(f"Could not create account. \nReason: {error}", "alert-danger")
            return redirect(url_for("add_admin_user"))

        flash(f"{admin_account.username}'s account has been created successfully!", "alert-success")

        return redirect(url_for("add_admin_user"))
    return render_template('admin/admin_register.html')


@app.route('/reset_password', methods=['POST', 'GET'])
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
                return redirect(url_for("customer_password_reset"))
        else:
            flash("Cannot reset password at the moment. Please contact us for help.", "alert-danger")
            return redirect(url_for("customer_password_reset"))

        flash("Your password has been successfully reset. Use new password to log in", "alert-info")
        return redirect(url_for("login"))

    return render_template('password_reset.html')


@app.route('/reset/<int:customer_id>')
def password_reset(customer_id):
    customer = Customers.query.filter_by(id=customer_id).first()
    customer.password = None
    db.session.commit()
    flash(f"{customer.fullname.split(' ')[0]}'s password has been reset. \nPlease inform them to set a new password.",
          "alert-info")
    return redirect(url_for('admin_view', view='customers'))


@app.route('/send_us_message', methods=['POST', 'GET'])
def send_comment():
    if request.method == 'POST':
        form = request.form
        comment = Messages(
            name=form['contact-name'],
            phone_number=form['contact-phone'],
            email_address=form['contact-email'],
            subject=form['contact-subject'],
            message=form['contact-message']
        )
        try:
            db.session.add(comment)
            db.session.commit()
            flash("Thank you for your message. We will get back to you as soon as we can.", "alert-info")
        except Exception as error:
            print(error)
            flash("Sorry, could not send message. Please try again later or call us", "alert-warning")
    return redirect(url_for('contact'))
