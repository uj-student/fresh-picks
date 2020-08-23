import sqlite3
import traceback


def get_connection():
    try:
        connection = sqlite3.connect('freshPicks.sqlite')
        print("Connected to DB")
        return connection
    except sqlite3.Error as error:
        print(f"Failed to connect: \nProblem -> {error}")


def close_connection(connection):
    if connection:
        connection.close()


def get_products():
    conn = get_connection()
    record = ""
    try:
        query = "select * from products order by name asc;"

        cursor = conn.cursor()
        cursor.execute(query)
        record = cursor.fetchall()
        cursor.close()
    except Exception as error:
        print(f"Failed to get products: \nProblem -> {error}")
    finally:
        close_connection(conn)
        if record:
            return record


# need a date created and date modified timestamp
def add_user(user_account):
    conn = get_connection()
    try:
        query = "insert into users (fullname, address, town, country, phone_number, email_address, gender, dob, " \
                "password, terms_and_conditions) values  (:fullname, :address, :town, :country, :phone_number, " \
                ":email_address, :gender, :dob, :password, :terms_and_conditions)"

        cursor = conn.cursor()
        cursor.execute(query,
                       (user_account.get_user_name(), user_account.get_user_address(), user_account.get_user_town(),
                        user_account.get_user_country(), user_account.get_user_phone_number(),
                        user_account.get_user_email_address(),
                        user_account.get_user_gender(), user_account.get_user_birthday(),
                        user_account.get_user_password(), user_account.get_user_terms_and_conditions()))
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        traceback.print_exc()
        print(f'Failed to add user: \nProblem -> {error}')
        raise Exception(error)
    finally:
        close_connection(conn)


def get_user_profile(user_phone):
    conn = get_connection()
    user_account = ""
    try:
        query = "select * from users where phone_number = ?;"
        cursor = conn.cursor()
        user_account = cursor.execute(query, (user_phone,)).fetchone()
        cursor.close()
    except Exception as error:
        traceback.print_exc()
        print()
        raise Exception(error)
    finally:
        close_connection(conn)

    return user_account


def get_all_customers():
    conn = get_connection()
    user_account_list = ""
    try:
        query = "select * from users"
        cursor = conn.cursor()
        user_account_list = cursor.execute(query).fetchall()
        cursor.close()
    except Exception as error:
        traceback.print_exc()
        print()
        raise Exception(error)
    finally:
        close_connection(conn)

    return user_account_list

def get_user_by_id(user_id):
    conn = get_connection()
    user_account = ""
    try:
        query = "select * from users where id = ?;"
        cursor = conn.cursor()
        user_account = cursor.execute(query, (user_id,)).fetchone()
        cursor.close()
    except Exception as error:
        traceback.print_exc()
        print()
        raise Exception(error)
    finally:
        close_connection(conn)

    return user_account


def is_unique(phone_number, email):
    conn = get_connection()
    unique = True
    try:
        query = "select * from users where phone_number = ? or email_address = ?;"
        cursor = conn.cursor()
        result = cursor.execute(query, (phone_number, email)).fetchall()
        cursor.close()
    except Exception:
        raise Exception
    finally:
        close_connection(conn)

    if len(result) > 0:
        unique = False
    return unique


# assumption is user won't be changing a lot of fields
def update_user(old_data, new_data):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if old_data.get_name() != new_data.get_name():
            query = "UPDATE users SET fullname = ? where id =? ;"
            cursor.execute(query, (new_data.get_name(), old_data.get_id()))
        if old_data.get_address() != new_data.get_address():
            query = "UPDATE users SET address = ? where id =? ;"
            cursor.execute(query, (new_data.get_address(), old_data.get_id()))
        if old_data.get_town() != new_data.get_town():
            query = "UPDATE users SET town = ? where id =? ;"
            cursor.execute(query, (new_data.get_town(), old_data.get_id()))
        if old_data.get_phone() != new_data.get_phone():
            query = "UPDATE users SET phone_number = ? where id =? ;"
            cursor.execute(query, (new_data.get_phone(), old_data.get_id()))
        if old_data.get_email() != new_data.get_email():
            query = "UPDATE users SET email_address = ? where id =? ;"
            cursor.execute(query, (new_data.get_email(), old_data.get_id()))
        if old_data.get_gender() != new_data.get_gender():
            query = "UPDATE users SET gender = ? where id =? ;"
            cursor.execute(query, (new_data.get_gender(), old_data.get_id()))
        if old_data.get_dob() != new_data.get_dob():
            query = "UPDATE users SET dob = ? where id =? ;"
            cursor.execute(query, (new_data.get_dob(), old_data.get_id()))
        conn.commit()
        cursor.close()
    except Exception:
        raise Exception
    finally:
        close_connection(conn)


def create_order(my_order):
    conn = get_connection()
    try:
        query = "insert into orders (customer_id, contents, total_price, delivery_address, additional_instructions) " \
                "VALUES (:customer_id, :contents, :price, :address, :instructions)"
        cursor = conn.cursor()
        cursor.execute(query, (my_order.get_customer_id(), my_order.get_contents(), my_order.get_total_price(),
                               my_order.get_delivery_address(), my_order.get_instructions()))
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        traceback.print_exc()
        print(f'Failed to add user: \nProblem -> {error}')
        raise Exception(error)
    finally:
        close_connection(conn)


def get_pending_orders():
    conn = get_connection()
    result = ""
    try:
        query = "select orders.id, fullname, contents, total_price, delivery_address, status, date from orders " \
                "inner join users u on orders.customer_id = u.id where status = ? and updated_status = ?;"
        cursor = conn.cursor()
        result = cursor.execute(query, ("pending", 0)).fetchall()
        cursor.close()
    except sqlite3.Error as error:
        traceback.print_exc()
        print(f'Failed to add user: \nProblem -> {error}')
        raise Exception(error)
    finally:
        close_connection(conn)
        return result

def update_order_status(order_id, old_status, new_status):
    conn = get_connection()
    try:
        query = "insert into orders_status(order_id, previous_status, current_status) values (:id, :old_status, :new_status);"
        cursor = conn.cursor()
        cursor.execute(query, (order_id, old_status, new_status))
        # this 2nd query might need to be a scheduled overnight query should performance dip
        query = "UPDATE orders SET updated_status = ? where id =? ;"
        cursor.execute(query, (1,order_id))
        conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        #need to test this... extensively!!!!
        conn.rollback()
        traceback.print_exc()
        print(f'Failed to add user: \nProblem -> {error}')
        raise Exception(error)
    finally:
        close_connection(conn)
