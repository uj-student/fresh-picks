import datetime

from flask import Blueprint, g, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from freshpicks import db
from freshpicks.FreshPicksUtilities import upload_picture
from freshpicks.databaseModels import AdminUsers, Orders, Customers, Products, Messages

admins = Blueprint('admins', __name__)
PER_PAGE_VIEW = 10


@admins.route('/admin', methods=['GET', "POST"])
def admin():
    if g.admins:
        return redirect(url_for('.admin_view', view='all_orders'))
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
        return redirect(url_for('.admin_view', view='all_orders'))
    return render_template('admin/admin_login.html')


@admins.route('/admin/<path:view>')
def admin_view(view):
    if not g.admins:
        return redirect(url_for('.admin'))
    page = request.args.get('page', 1, type=int)
    customer_id = request.args.get('customer_id', 0, type=int)

    if "orders" in view:
        orders = ""  # need this to handle the filter the orders  in the view
        order_type = "all_orders"
        if view == "pending_orders":
            orders = Orders.query.filter_by(status="pending").paginate(per_page=PER_PAGE_VIEW, page=page)
            order_type = "pending_orders"
        elif view == "completed_orders":
            orders = Orders.query.filter_by(status="complete").paginate(per_page=PER_PAGE_VIEW, page=page)
            order_type = "completed_orders"
        elif view == "cancelled_orders":
            orders = Orders.query.filter_by(status="cancel").paginate(per_page=PER_PAGE_VIEW, page=page)
            order_type = "cancelled_orders"
        elif view == "all_orders":
            orders = Orders.query.paginate(per_page=PER_PAGE_VIEW, page=page)
        elif view == "customers_orders":
            orders = Orders.query.filter_by(customer_id=customer_id).order_by(Orders.date_ordered.desc())\
                .paginate(per_page=PER_PAGE_VIEW, page=page)
            order_type = "customers_orders"
        return render_template('admin/manage_orders.html', order_type=order_type, orders_list=orders, customer_id=customer_id)
    elif view == "customers":
        customer_list = Customers.query.order_by(Customers.fullname.asc()).paginate(per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_customers.html', customer_list=customer_list)
    elif view == "admin_users":
        admin_list = AdminUsers.query.order_by(AdminUsers.username.asc()).paginate(per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_users.html', admin_list=admin_list)
    elif view == "products":
        product_list = Products.query.order_by(Products.is_box.desc(), Products.name.asc()).paginate(
            per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_products.html', product_list=product_list)
    elif view == "customer_messages":
        status = request.args.get('msg_status') if request.args.get('msg_status') else 'open'
        messages = Messages.query.filter_by(status=status).order_by(Messages.date_sent.asc()).paginate(
            per_page=PER_PAGE_VIEW, page=page)
        return render_template('admin/manage_comments.html', msg_status=status, messages_list=messages)
    return render_template('admin/manage_products.html', product_list=[])


def get_customer_orders(customer_id):
    return Orders.query.filter_by(customer_id=customer_id).order_by(Orders.date_ordered.desc()) \
        .paginate(per_page=PER_PAGE_VIEW, page=request.args.get('page', 1, type=int))


@admins.route('/admin/mark_complete', methods=['POST'])
def mark_complete():
    if not g.admins:
        return redirect(url_for('.admin'))
    if request.method == 'POST':
        new_status = request.form['_order_status']
        current_status = request.form['_current_status']
        order_id = request.form['_order_id']

        my_order = Orders.query.filter_by(id=order_id, status=current_status) \
            .first()
        update_time = datetime.datetime.now()
        try:
            my_order.status = new_status
            if new_status == "pending":
                my_order.back_to_pending = update_time
            elif new_status == "complete":
                my_order.date_completed = update_time
            elif new_status == "cancel":
                my_order.date_cancelled = update_time
            db.session.commit()
            flash(f"{my_order.buyer.fullname}'s order has been updated.", "alert-info")
        except Exception as error:
            pass
    return redirect(url_for('.admin_view', view="pending_orders"))


@admins.route('/admin/remove/<int:product_id>')
def toggle_product_display(product_id):
    if not g.admins:
        return redirect(url_for('.admin'))

    product = Products.query.filter_by(id=product_id).first()
    display_status = product.is_displayed

    if display_status:
        product.is_displayed = False
    else:
        product.is_displayed = True

    db.session.commit()
    return redirect((url_for('.admin_view', view="products")))


@admins.route('/admin/products/add', methods=['POST', 'GET'])
def add_product():
    if not g.admins:
        return redirect(url_for('.admin'))
    if request.method == "POST":
        req = request.form
        image_location = upload_picture(request.files['display-image'])
        new_product = Products(
            name=req['product-name'],
            description=req['product-description'],
            cost_price=req['cost-price'],
            sell_price=req['sell-price'],
            image_location=image_location,
            is_box=False if req['type'] == "extra" else True,
            is_displayed=True if req['display'] == "yes" else False
        )
        try:
            db.session.add(new_product)
            db.session.commit()
        except Exception as error:
            flash(f"Could not add product. \nReason: {error}", "alert-danger")
            return redirect(url_for(".add_product"))

        flash(f"{new_product.name} added successfully.", "alert-success")
        return redirect(url_for('.add_product'))
    return render_template('admin/add_products.html')


@admins.route('/admin/products/edit', methods=['POST', 'GET'])
def edit_product():
    if not g.admins:
        return redirect(url_for('.admin'))
    p_id = request.args.get('product_id', 1, type=int)
    product = Products.query.filter_by(id=p_id).first()

    if request.method == "POST":
        req = request.form
        product.name = req['product-name']
        product.description = req['product-description']
        product.sell_price = req['sell-price']
        product.cost_price = req['cost-price']
        product.is_box = False if req['product-type'] == "extra" else True
        product.is_displayed = True if req['display'] == "yes" else False

        try:
            db.session.commit()
        except Exception as error:
            flash(f"Could not add product. \nReason: {error}", "alert-danger")
            return redirect(url_for(".admin_views", view='products'))

        flash(f"{product.name} successfully edited.", "alert-success")
        return redirect(url_for(".admin_view", view='products'))
    return render_template('admin/admin_edit_products.html', product=product)


@admins.route('/admin/users/add', methods=['POST', 'GET'])
def add_admin_user():
    if not g.admins:
        return redirect(url_for('.admin'))
    if request.method == "POST":
        req = request.form

        if len(req['username']) < 6:
            flash("Username must be at least 6 characters long. Please try again.", "alert-warning")
            # return redirect(url_for("add_admin_user"))
            return render_template('admin/admin_register.html')

        if len(req['password']) < 10:
            flash("Password must be at least 10 characters. Please choose a strong password.", "alert-danger")
            # return render_template('admin/admin_register.html')
            return redirect(url_for(".add_admin_user"))

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
            return redirect(url_for(".add_admin_user"))

        flash(f"{admin_account.username}'s account has been created successfully!", "alert-success")

        return redirect(url_for(".add_admin_user"))
    return render_template('admin/admin_register.html')


@admins.route('/admin/reset/<int:customer_id>')
def password_reset(customer_id):
    customer = Customers.query.filter_by(id=customer_id).first()
    customer.password = None
    db.session.commit()
    flash(f"{customer.fullname.split(' ')[0]}'s password has been reset. \nPlease inform them to set a new password.",
          "alert-info")
    return redirect(url_for('.admin_view', view='customers'))


def setupAdminSession(adminUser):
    session.clear()
    session['admin_username'] = adminUser.username
    session['name'] = adminUser.name


@admins.before_request
def before_request():
    g.admins = None
    if 'admin_username' in session:
        g.admins = session['admin_username']


@admins.route('/mark_comment_complete/<int:comment_id>', methods=['POST'])
def update_message(comment_id):
    if request.method == 'POST':
        comment = Messages.query.filter_by(id=comment_id).first()
        comment.status = 'closed'
        comment.date_updated = datetime.datetime.now()
        db.session.commit()
        flash(f"Message from {comment.name} has been closed.", "alert-info")
        return redirect(url_for('.admin_view', view='customer_messages'))
    return render_template('manage_comments.html')
