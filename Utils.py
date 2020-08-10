import FreshPicksObjects as my_objects
def convert_to_Product(database_result):
    basket_items = []
    extra_items = []
    for result in database_result:
        new_entry = my_objects.ProductObject(result[1], result[2], result[3], result[4], result[5])
        if new_entry.is_main:
            basket_items.append(new_entry)
        else:
            extra_items.append(new_entry)
    return basket_items, extra_items

def convert_to_User(database_record):
    return my_objects.User(

        database_record[1],
        database_record[2],
        database_record[3],
        database_record[4],
        database_record[5],
        database_record[7],
        database_record[8],
        database_record[9],
        database_record[10],
        database_record[6], # email column
        database_record[0] # db id

    )
