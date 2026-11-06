# stage 1
# Card anatomy
import random
import sqlite3

with sqlite3.connect('card.s3db') as conn:
    cur = conn.cursor()

create_table = """CREATE TABLE IF NOT EXISTS card (
    id INTEGER PRIMARY KEY,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
);"""

# Executes some SQL query
cur.execute(create_table)

# After making some changes in DB don't forget to commit them!
conn.commit()

menu = """1. Create an account
2. Log into account
0. Exit"""
print(menu)

submenu = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
"""


# 16 digit
# iin - first 6 digit
# customer account number from 7th digit till 15th
# check sum - 16th digit


def create_pin_number():
    pin_number = ''
    for i in range(0, 4):
        pin_number += str(random.randint(1, 9))
    return pin_number


# Stage 2
# Luhn algorithm
def create_card_number(iin=400000):
    while True:
        customer_account_number = ''
        for i in range(0, 10):
            customer_account_number += str(random.randint(1, 9))
        card_number = str(iin) + customer_account_number
        # split all digits
        after_split = [int(d) for d in card_number]
        last_element = after_split.pop(-1)
        # multiply odd digits by 2
        multiplied_odd_digits_by_two = [val * 2 if i % 2 == 0 else val for i, val in enumerate(after_split)]

        # Subtract 9 from numbers over 9
        subtracted_nine_from_numbers_over_nine = [val - 9 if val > 9 else val for val in multiplied_odd_digits_by_two]
        # add all numbers
        addition_result = sum(subtracted_nine_from_numbers_over_nine) + last_element
        # calculate check sum
        if addition_result % 10 == 0:
            return card_number
        else:
            continue


def create_an_account():
    print("Your card has been created")
    print("Your card number:")
    created_card_number = create_card_number()
    print(created_card_number)
    print("Your card PIN:")
    created_pin_number = create_pin_number()
    print(created_pin_number)
    balance = 0
    return created_card_number, created_pin_number, balance


def add_income(credit_card_number):
    print("Enter income:")
    income = int(input())
    update_db = f"""
            UPDATE card 
            SET balance = balance + {income}
            WHERE number = {credit_card_number};
            """
    cur.execute(update_db)
    conn.commit()
    print("Income was added!")


def luhn_validator(ccn):
    after_split = [int(d) for d in ccn]
    last_element = after_split.pop(-1)
    # multiply odd digits by 2
    multiplied_odd_digits_by_two = [val * 2 if i % 2 == 0 else val for i, val in enumerate(after_split)]

    # Subtract 9 from numbers over 9
    subtracted_nine_from_numbers_over_nine = [val - 9 if val > 9 else val for val in multiplied_odd_digits_by_two]
    # add all numbers
    addition_result = sum(subtracted_nine_from_numbers_over_nine) + last_element
    # calculate check sum
    if addition_result % 10 == 0:
        return ccn
    else:
        print("Probably you made a mistake in the card number. Please try again!")
        return None


def do_transfer(current_account_card_number):
    print()
    print("Transfer")
    print("Enter card number:")
    card_number = input()
    if card_number == current_account_card_number:
        print("You can't transfer money to the same account!")
    luhn_alg = luhn_validator(card_number)
    if card_number == luhn_alg:
        searched_card_no = f"""SELECT * from card WHERE number = "{card_number}";"""
        cur.execute(searched_card_no)
        conn.commit()
        result = cur.fetchall()
        if len(result) == 0:
            print("Such a card does not exist.")
        elif len(result) == 1:
            print("Enter how much money you want to transfer:")
            how_much_money = int(input())
            search_current_card_number_balance = f"""SELECT balance FROM card WHERE number = "{current_account_card_number}";"""
            cur.execute(search_current_card_number_balance)
            conn.commit()
            balance_value = cur.fetchone()[0]
            if balance_value > how_much_money:
                update_donor = f"""
                            UPDATE card 
                            SET balance = balance - {how_much_money}
                            WHERE number = "{current_account_card_number}";
                            """
                cur.execute(update_donor)
                conn.commit()
                update_acceptor = f"""
                                UPDATE card
                                SET balance = balance + {how_much_money}
                                WHERE number = "{card_number}";
                                """
                cur.execute(update_acceptor)
                conn.commit()
                print("Success!")
            else:
                print("Not enough money!")


def close_account(account_to_close_based_on_valid_card_no):
    before_deletion = f"""SELECT * FROM card;"""
    cur.execute(before_deletion)
    conn.commit()
    no_of_rows_before = len(cur.fetchall())
    delete_account = f"""
    DELETE FROM card WHERE number = "{account_to_close_based_on_valid_card_no}";"""
    cur.execute(delete_account)
    conn.commit()
    after_deletion = f"""SELECT * FROM card;"""
    cur.execute(after_deletion)
    conn.commit()
    no_of_rows_after = len(cur.fetchall())
    if no_of_rows_before == no_of_rows_after + 1:
        print("The account has been closed!")
        return True
    else:
        return False


while True:
    user_input = input()
    print()
    if user_input == "0":
        print("Bye!")
        exit()
    elif user_input == "1":
        card_no, pin_no, balance_of_the_account = create_an_account()
        insert_data_to_db = f"""
        INSERT INTO card (number, pin, balance) 
        VALUES ({card_no}, {pin_no}, {balance_of_the_account});
        """
        cur.execute(insert_data_to_db)
        conn.commit()
        print(menu)
    elif user_input == "2":
        print("Enter your card number:")
        your_card_number = input()
        print("Enter your PIN:")
        your_pin_number = input()
        cur.execute(f'SELECT * FROM card WHERE number = {your_card_number} AND pin = {your_pin_number};')
        row = cur.fetchall()
        if len(row) == 0:
            print()
            print("Wrong card number or PIN!")
            print()
            print(menu)
            continue
        else:
            print()
            print("You have successfully logged in!")
            print()
            print(submenu)
            while True:
                sub_menu_user_input = input()
                if sub_menu_user_input == "1":
                    print()
                    print(f"Balance: {row[0][3]}")
                    print()
                    print(submenu)
                    continue
                elif sub_menu_user_input == "2":
                    add_income(your_card_number)
                    print()
                    print(submenu)
                    continue
                elif sub_menu_user_input == "3":
                    do_transfer(your_card_number)
                    print()
                    print(submenu)
                    continue
                elif sub_menu_user_input == "4":
                    is_account_closed = close_account(your_card_number)
                    if is_account_closed:
                        break
                elif sub_menu_user_input == "5":
                    print()
                    print("You have successfully logged out!")
                    break
                elif sub_menu_user_input == "0":
                    print()
                    print("Bye!")
                    exit()
            print()
            print(menu)
