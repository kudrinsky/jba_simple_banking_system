import random
import sqlite3
db = sqlite3.connect('card.s3db')
create_table_query = """CREATE TABLE IF NOT EXISTS card (
id INTEGER PRIMARY KEY,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
)"""
cur = db.cursor()
cur.execute(create_table_query)
db.commit()
state = 'main'
current_customer = []


def create():
    card = [4, 0, 0, 0, 0, 0] + [random.randint(0, 9) for i in range(9)]
    card_check = [card[i] * 2 if i % 2 == 0 else card[i] for i in range(len(card))]
    card_check = [num if num < 10 else num - 9 for num in card_check]
    if sum(card_check) % 10 != 0:
        card.append(10 - sum(card_check) % 10)
    else:
        card.append(0)
    card_number = ''.join([str(item) for item in card])
    pin = ''.join([str(random.randint(0, 9)) for i in range(4)])
    print(f'\nYour card has been created\nYour card number:\n{card_number}')
    print(f'Your card PIN:\n{pin}\n')
    cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card_number, pin))
    db.commit()
    menu()


def login():
    global state, current_customer
    card = input('\nEnter your card number:\n')
    pin = input('Enter your PIN:\n')
    cur.execute(f'SELECT number, pin FROM card WHERE number = {card}')
    current_customer = cur.fetchall()
    if current_customer != [] and current_customer[0][1] == pin:
        print('\nYou have successfully logged in!\n')
        state = 'login'
    else:
        print('\nWrong card number or PIN!\n')
        current_customer = []
    menu()


def transfer():
    transfer_card = input('\nTransfer\nEnter card number:\n')
    if transfer_card == current_customer[0][0]:
        print("You can't transfer money to the same account!\n")
        menu()
    else:
        transfer_check = [int(transfer_card[i]) * 2 if i % 2 == 0 else int(transfer_card[i])
                          for i in range(len(transfer_card) - 1)]
        transfer_check = [num if num < 10 else num - 9 for num in transfer_check]
        check = (sum(transfer_check) + int(transfer_card[-1])) % 10
        print(check)
        if check != 0:
            print('Probably you made mistake in the card number. Please try again!\n')
            menu()
        else:
            cur.execute(f'SELECT number, balance FROM card WHERE number = {transfer_card}')
            trans_query = cur.fetchall()
            if not trans_query:
                print('Such a card does not exist.\n')
                menu()
            else:
                transfer_sum = input('Enter how much money you want to transfer:\n')
                cur.execute(f'SELECT balance FROM card WHERE number = {current_customer[0][0]}')
                balance = cur.fetchall()
                if int(transfer_sum) > balance[0][0]:
                    print('Not enough money!\n')
                    menu()
                else:
                    cur.execute(f'UPDATE card SET balance = balance - {int(transfer_sum)} WHERE number = {current_customer[0][0]}')
                    cur.execute(f'UPDATE card SET balance = balance + {int(transfer_sum)} WHERE number = {transfer_card}')
                    db.commit()
                    print('Success!\n')
                    menu()


def menu():
    global state, current_customer
    if state == 'main':
        current_choice = input('1. Create an account\n2. Log into account\n0. Exit\n')
        if current_choice == '1':
            create()
        elif current_choice == '2':
            login()
        else:
            db.close()
            print('\nBye!')
    elif state == 'login':
        current_choice = input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n')
        if current_choice == '1':
            cur.execute(f'SELECT balance FROM card WHERE number = {current_customer[0][0]}')
            balance = cur.fetchall()
            print(f'\nBalance: {balance[0][0]}\n')
            menu()
        elif current_choice == '2':
            income = input('\nEnter income:\n')
            cur.execute(f'UPDATE card SET balance = balance + {int(income)} WHERE number = {current_customer[0][0]}')
            db.commit()
            print('Income was added!\n')
            menu()
        elif current_choice == '3':
            transfer()
        elif current_choice == '4':
            cur.execute(f'DELETE FROM card WHERE number = {current_customer[0][0]}')
            db.commit()
            state = 'main'
            current_customer = []
            print()
            menu()
        elif current_choice == '5':
            state = 'main'
            current_customer = []
            print()
            menu()
        else:
            db.close()
            print('\nBye!')


menu()
