import datetime

from flask_login import UserMixin

from freshpicks import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Customers.query.get(int(user_id))


class Customers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    fullname = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    town = db.Column(db.String(), nullable=False)
    country = db.Column(db.String(), nullable=False)
    phone_number = db.Column(db.String(), nullable=False, unique=True)
    email_address = db.Column(db.String(), unique=True, nullable=True)
    gender = db.Column(db.String(), nullable=False)
    dob = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=True)
    terms_and_conditions = db.Column(db.Boolean(), nullable=False)
    date_registered = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow(), nullable=False)
    orders = db.relationship('Orders', backref='buyer', lazy=True)

    def __repr__(self):
        return f"Customer('{self.id}', '{self.fullname}', '{self.address}', '{self.town}', '{self.country}', " \
               f"'{self.phone_number}', '{self.email_address}', '{self.gender}', '{self.dob}', '{self.terms_and_conditions}'," \
               f"'{self.date_registered}')"


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customers.id'), nullable=False)
    order = db.Column(db.String(), nullable=False)
    total_price = db.Column(db.Float(), nullable=False)
    delivery_address = db.Column(db.String(), nullable=False)
    date_ordered = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow(), nullable=False)
    additional_instructions = db.Column(db.String(), nullable=True)
    status = db.Column(db.String(), nullable=False, default="pending")
    date_completed = db.Column(db.TIMESTAMP(), nullable=True)
    date_cancelled = db.Column(db.TIMESTAMP(), nullable=True)

    def __repr__(self):
        return f"Order('{self.id}', '{self.customer_id}', '{self.order}', '{self.total_price}', " \
               f"'{self.delivery_address}', '{self.date_ordered}', '{self.additional_instructions}', '{self.status}', " \
               f"'{self.date_completed}', '{self.date_cancelled}')"


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=True)
    price = db.Column(db.Float(), nullable=False)
    image_location = db.Column(db.String(), unique=True, nullable=False)
    is_basket_item = db.Column(db.Boolean(), default=False, nullable=False)
    is_displayed = db.Column(db.Boolean(), default=False, nullable=False)

    def __repr__(self):
        return f"Product('{self.id}', '{self.name}', '{self.description}', '{self.price}', '{self.image_location}', " \
               f"'{self.is_basket_item}', {self.is_displayed})"


class AdminUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    cellphone_number = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    email_address = db.Column(db.String(), unique=True, nullable=False)
    date_created = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f"Admin('{self.id}', '{self.username}', '{self.cellphone_number}', '{self.name}', '{self.email_address}', " \
               f"'{self.date_created}')"


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(), nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String, nullable=True)
    subject = db.Column(db.String, nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String, nullable=False, default='open')
    date_sent = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow(), nullable=False)
    date_updated = db.Column(db.TIMESTAMP(), nullable=True)
