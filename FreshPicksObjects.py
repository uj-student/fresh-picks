import FreshPicksUtilities

class ProductObject:
    def __init__(self, product_id, name, description, price, image=None, is_main=False, is_display=False):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.is_main = is_main
        self.is_display = is_display

    def get_product_id(self):
        return self.product_id

    def get_product_name(self):
        return self.name

    def get_product_description(self):
        return self.description

    def get_product_price(self):
        return self.price

    def get_product_image(self):
        return self.image

    def get_is_main(self):
        return self.is_main

    def get_is_display(self):
        return self.is_display

class User:
    def __init__(self, fullname, address, town, country, phone_number, gender, dob, password, terms_and_conditions, email_address="", db_id =0):
        self.id = db_id
        self.name = fullname
        self.address = address
        self.town = town
        self.country = country
        self.phone_number = phone_number
        self.gender =gender
        self.birthday = dob
        self.password = password
        self.accepted = terms_and_conditions
        self.email = email_address

    def get_user_id(self):
        return self.id

    def get_user_name(self):
        return self.name

    def get_user_first_name(self):
        return self.name.split(' ')[0]

    def get_user_address(self):
        return self.address

    def get_user_town(self):
        return self.town

    def get_full_address(self):
        return f"{self.address, self.town}"

    def get_user_country(self):
        return self.country

    def get_user_phone_number(self):
        return self.phone_number

    def get_user_email_address(self):
        return self.email

    def get_user_gender(self):
        return self.gender

    def get_user_birthday(self):
        return self.birthday

    def get_user_password(self):
        return self.password

    def get_user_terms_and_conditions(self):
        return self.accepted

    def set_user_name(self, name):
        self.name = name

    def set_user_address(self, address):
        self.address = address

    def set_user_town(self, town):
        self.town = town

    def set_user_country(self, country):
        self.country = country

    def set_user_phone_number(self, phone_number):
        self.phone_number = phone_number

    def set_user_email_address(self, email):
        self.email = email

    def set_user_gender(self, gender):
        self.gender = gender

    def set_user_birthday(self, birthday):
        self.birthday = birthday

    def set_user_password(self, password):
        self.password = password

    def set_user_terms_and_conditions(self, accepted):
        self.accepted = accepted

    def set_user_id(self, db_id):
        self.id = db_id

class UserUpdatedDetails:
    def __init__(self, _id, fullname, address, town, phone, email, gender, dob):
        self._id = _id
        self.name = fullname
        self.address = address
        self.town = town
        self.phone = phone
        self.email = email
        self.gender = gender
        self.dob = dob

    def get_id(self):
        return self._id

    def get_name(self):
        return self.name

    def get_address(self):
        return self.address

    def get_town(self):
        return self.town

    def get_phone(self):
        return self.phone

    def get_email(self):
        return self.email

    def get_gender(self):
        return self.gender

    def get_dob(self):
        return self.dob

class Orders:
    def __init__(self, customer_id, contents, total_price, delivery_address, date_created, instructions=None,
                 status="pending", order_id=0):
        self.order_id = order_id
        self.customer_id = customer_id
        self.contents = contents
        self.total_price = total_price
        self.delivery_address = delivery_address
        self.instructions = instructions
        self.status = status
        self.date_created = date_created

    def get_order_id(self):
        return self.order_id

    def get_customer_id(self):
        return self.customer_id

    def get_contents(self):
        return self.contents

    def get_total_price(self):
        return self.total_price

    def get_delivery_address(self):
        return self.delivery_address

    def get_instructions(self):
        return self.instructions

    def get_status(self):
        return FreshPicksUtilities.capitaliseName(self.status)

    def get_date_created(self):
        return self.date_created