import time
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="obie9090",
    database="mybank")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    password VARCHAR(255),
    balance FLOAT)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_no INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    type VARCHAR(255),
    amount FLOAT,
    FOREIGN KEY (account_id) REFERENCES accounts(id))
""")

class Account:
    def __init__(self, id, name, password, balance=0):
        self.id = id
        self.name = name
        self.password = password
        self._balance = balance

    def deposit(self, amount):
        self._balance += amount
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, self.id))
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'deposit', %s)", (self.id, amount))
        db.commit()

    def withdraw(self, amount):
        self._balance -= amount
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, self.id))
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'withdrawal', %s)", (self.id, amount))
        db.commit()

    def check_balance(self):
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (self.id,))
        balance = cursor.fetchone()[0]
        return balance

    def transfer(self, receiver_account, amount):
        self._balance -= amount
        receiver_account._balance += amount
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, self.id))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, receiver_account.id))
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'transfer out', %s)", (self.id, amount))
        cursor.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'transfer in', %s)", (receiver_account.id, amount))
        db.commit()

    def display_transactions(self):
        cursor.execute("SELECT type, amount FROM transactions WHERE account_id = %s", (self.id,))
        transactions = cursor.fetchall()
        return transactions

class Bank:
    def __init__(self):
        self.accounts = {}

    def open_new_account(self, id, name, password, initial_deposit=0):
        cursor.execute("SELECT id FROM accounts WHERE id = %s", (id,))
        if cursor.fetchone():
            return "Account already exists❌"
        else:
            cursor.execute("INSERT INTO accounts (id, name, password, balance) VALUES (%s, %s, %s, %s)", (id, name, password, initial_deposit))
            db.commit()
            return "Account created successfully✔️"

    def login(self, id, password):
        cursor.execute("SELECT id, name, password, balance FROM accounts WHERE id = %s AND password = %s", (id, password))
        account_data = cursor.fetchone()
        if account_data:
            return "Login successful✔️", Account(*account_data)
        else:
            return "Invalid account ID or password", None

    def quit(self):
        return "Thank you for using ARKHAM Bank🩵"

def main():
    bank = Bank()

    while True:
        print("=" * 30)
        print("🦇 Welcome to ARKHAM Bank🦇")
        print("1. Login")
        print("2. Open New Account")
        print("3. Quit")
        print("=" * 30)
        choice = input("Please choose an option: ")

        if choice == '1':
            id = input("Enter your ID: ")
            password = input("Enter your password: ")
            print("Logging in...⌛")
            time.sleep(1.5)
            result, account = bank.login(id, password)
            print(result)
            while account:
                print(f"\nWelcome, {account.name.title()}👋")
                print("1. Deposit")
                print("2. Withdraw")
                print("3. Check Balance")
                print("4. Transfer Money")
                print("5. Show Transaction History")
                print("6. Logout")
                user_choice = input("Please choose an option: ")

                if user_choice == '1':
                    amount = float(input("Enter the amount to deposit: "))
                    account.deposit(amount)
                    print(f"Deposited {amount:.2f}💸 successfully")

                elif user_choice == '2':
                    amount = float(input("Amount to withdraw: "))
                    if amount > account.check_balance():
                        print("Insufficient balance❌")
                    else:
                        account.withdraw(amount)
                        print(f"Withdrawn {amount:.2f}💸 Successfully!")

                elif user_choice == '3':
                    print(f'Your balance is:{account.check_balance():.2f}💸')

                elif user_choice == '4':
                    receiver_id = input('Enter receiver account ID: ')
                    if receiver_id == str(account.id):
                        print("Cannot transfer to the same account❌")
                    else:
                        cursor.execute("SELECT * FROM accounts WHERE id = %s", (receiver_id,))
                        receiver_data = cursor.fetchone()
                        if receiver_data is not None:
                            receiver_acc = Account(*receiver_data)
                            amount = float(input('Enter amount to transfer: '))
                            if amount > account.check_balance():
                                print("Insufficient balance❌")
                            else:
                                account.transfer(receiver_acc, amount)
                                print("Transfer Successful✔️")
                        else:
                            print("Account not found❌")

                elif user_choice == '5':
                    transactions = account.display_transactions()
                    if transactions:
                        print("Transactions:")
                        for transaction in transactions:
                            print(transaction)
                    else:
                        print("No transaction history available")

                elif user_choice  == '6':
                    print("Logging out...⌛")
                    time.sleep(2)
                    account = None
                    print("Logged out successfully🦇")
                    break
                else:
                    print("Invalid choice! Please try again.")

        elif choice == '2':
            id = input("Enter your personal ID: ")
            name = input("Enter your name: ")
            password = input("Create a password: ")
            initial_deposit = float(input("Enter initial deposit amount: "))
            print("Opening new account...⌛")
            time.sleep(1.5)
            result = bank.open_new_account(id, name, password, initial_deposit)
            print(result)

        elif choice == '3':
            print(bank.quit())
            time.sleep(1.5)
            break

if __name__ == "__main__":
    main()