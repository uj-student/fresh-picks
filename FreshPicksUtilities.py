import stringcase

import FreshPicksObjects as my_objects


def convert_to_Product(database_result):
    basket_items = []
    extra_items = []
    for result in database_result:
        new_entry = my_objects.ProductObject(result[0], result[1], result[2], result[3], result[4], result[5])
        if new_entry.get_is_main():
            basket_items.append(new_entry)
        else:
            extra_items.append(new_entry)
    return basket_items, extra_items


def convert_to_User(database_record):
    return my_objects.User(
        fullname=database_record[1],
        address=database_record[2],
        town=database_record[3],
        country=database_record[4],
        phone_number=database_record[5],
        gender=database_record[7],
        dob=database_record[8],
        password=database_record[9],
        terms_and_conditions=database_record[10],
        email_address=database_record[6],  # email column
        db_id=database_record[0]  # db id
    )


def convert_to_order():
    # TODO
    pass


def capitaliseName(name):
    return stringcase.capitalcase(name)


def formatToCurrency(amount):
    return "%.2f".format(amount)
