import os
import time
from PIL import Image


from flask import Blueprint, g, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from freshpicks import db
from freshpicks.databaseModels import AdminUsers, Orders, Customers, Products, Messages

admins = Blueprint('admins', __name__)
PER_PAGE_VIEW =10

@admins.route('/admin', methods=['GET', "POST"])
def admin():
    if g.admins:
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


@admins.route('/admin/<path:view>')
def admin_view(view):
    if not g.admins:
        return redirect(url_for('admins.admin'))
    page = request.args.get('page', 1, type=int)

    if "orders" in view:
        orders = ""  # need this to handle the filter in the view
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
        admin_list = AdminUsers.query.order_by(AdminUsers.username.asc()).paginate(per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_users.html', admin_list=admin_list)
    elif view == "products":
        product_list = Products.query.order_by(Products.is_basket_item.desc(), Products.name.asc()).paginate(
            per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_products.html', product_list=product_list)
    elif view == "customer_messages":
        messages_list = Messages.query.order_by(Messages.date_sent.asc()).paginate(per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_comments.html', messages_list=messages_list)
    return render_template('admin/manage_products.html', product_list=[])


@admins.route('/admin/mark_complete', methods=['POST'])
def mark_complete():
    if not g.admins:
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


@admins.route('/admin/remove/<int:product_id>')
def toggle_product_display(product_id):
    if not g.admins:
        return redirect(url_for('admin'))

    product = Products.query.filter_by(id=product_id).first()
    display_status = product.is_displayed

    if display_status:
        product.is_displayed = False
    else:
        product.is_displayed = True

    db.session.commit()
    return redirect((url_for('admin_view', view="products")))


@admins.route('/admin/products/add', methods=['POST', 'GET'])
def add_product():
    if not g.admins:
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


@admins.route('/admin/users/add', methods=['POST', 'GET'])
def add_admin_user():
    if not g.admins:
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


@admins.route('/admin/reset/<int:customer_id>')
def password_reset(customer_id):
    customer = Customers.query.filter_by(id=customer_id).first()
    customer.password = None
    db.session.commit()
    flash(f"{customer.fullname.split(' ')[0]}'s password has been reset. \nPlease inform them to set a new password.",
          "alert-info")
    return redirect(url_for('admin_view', view='customers'))

def setupAdminSession(adminUser):
    session.clear()
    session['admin_username'] = adminUser.username
    session['name'] = adminUser.name


@admins.before_request
def before_request():
    g.user = None
    g.admins = None

    if 'admin_username' in session:
        g.admins = session['admin_username']