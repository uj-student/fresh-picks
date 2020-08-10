class ProductObject:
    def __init__(self, name, description, price, image=None, is_main=False):
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.is_main = is_main

    def get_product_name(self):
        return self.name

    def get_product_description(self):
        return self.description

    def get_product_price(self):
        return self.price

    def get_product_image(self):
        return self.image

    def is_main(self):
        return  self.is_main

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

    def get_user_address(self):
        return self.address

    def get_user_town(self):
        return self.town

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