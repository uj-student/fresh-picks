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
        user_account = cursor.execute(query, (user_phone, )).fetchone()
        cursor.close()

    except Exception as error:
        traceback.print_exc()
        print()
        raise Exception(error)
    finally:
        close_connection(conn)

    return user_account