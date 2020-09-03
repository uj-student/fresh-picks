from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import logout_user

from freshpicks.databaseModels import Products

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('index.html')


@main.route('/logout')
def logout():
    goto = ""
    # if g.user:
    #     goto = "home"
    # elif g.admin:
    #     goto = "admin"
    session.clear()
    logout_user()
    return redirect(url_for('home'))


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
