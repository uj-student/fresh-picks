import time

from app import db


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    fullname = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    town = db.Column(db.String(), nullable=False)
    country = db.Column(db.String(), nullable=False)
    phone_number = db.Column(db.String(), nullable=False, unique=True)
    email_address = db.Column(db.String(), unique=True, nullable=True)
    gender = db.Column(db.String(), nullable=False)
    dob = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    terms_and_conditions = db.Column(db.Boolean(), nullable=False)
    date_registered = db.Column(db.TIMESTAMP(), default=time.time(), nullable=False)
    orders = db.relationship('Orders', backref='buyer', lazy=True)

    def __repr__(self):
        return self


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    order = db.Column(db.String(), nullable=False)
    total_price = db.Column(db.Float(), nullable=False)
    delivery_address = db.Column(db.String(), unique=True, nullable=False)
    date_ordered = db.Column(db.TIMESTAMP(), default=time.time(), nullable=False)
    additional_instructions = db.Column(db.String(), nullable=True)
    status = db.Column(db.String(), nullable=False, default="pending")
    date_updated = db.Column(db.TIMESTAMP(), default=time.time(), nullable=False)

    def __repr__(self):
        return self


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=True)
    price = db.Column(db.Float(), nullable=False)
    image_location = db.Column(db.String(), unique=True, nullable=False)
    is_basket_item = db.Column(db.Boolean(), default=False, nullable=False)
    is_displayed = db.Column(db.Boolean(), default=False, nullable=False)

    def __repr__(self):
        return self

class AdminUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    cellphone_number = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    date_created = db.Column(db.TIMESTAMP(), default=time.time(), nullable=False)
    email_address = db.Column(db.String(), unique=True, nullable=False)

    def __repr__(self):
        return self