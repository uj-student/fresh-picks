from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import logout_user

from freshpicks import db
from freshpicks.databaseModels import Products, Messages

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('index.html')


@main.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('.home'))


@main.route('/contact')
def contact():
    return render_template('contact.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/test')
def shop():
    return render_template('shop.html')


@main.route('/products')
def products():
    product_list = ''
    try:
        product_list = Products.query.filter_by(is_displayed=True)
    except Exception as error:
        print(error)
    basket_display_list = []
    extras_display_list = []

    if product_list:
        for item in product_list:
            if item.is_basket_item:
                basket_display_list.append(item)
            else:
                extras_display_list.append(item)
    return render_template('products.html', baskets=basket_display_list, extras=extras_display_list)


@main.route('/send_us_message', methods=['POST', 'GET'])
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
    return redirect(url_for('.contact'))