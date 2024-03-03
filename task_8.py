from collections import UserDict
from datetime import datetime
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def validate(self):
        return True  # Базовий метод, буде перевизначено у підкласах

class Name(Field):
    def validate(self):
        return bool(self.value.strip())  # Перевіряємо, чи ім'я не порожнє

class Phone(Field):
    def validate(self):
        # Перевіряємо, чи має номер телефону правильний формат (10 цифр)
        return len(str(self.value)) == 10 and str(self.value).isdigit()

    def __init__(self, value):
        super().__init__(value)
        if not self.validate():
            raise ValueError("Invalid phone number format")

class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевіряємо правильність формату та перетворюємо рядок на об'єкт datetime
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = value

    def as_datetime(self):
        # Повертаємо об'єкт datetime
        return datetime.strptime(self.value, "%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p.value) for p in self.phones)}, birthday: {self.birthday.value if self.birthday else 'None'}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book):
    name, phone = args
    if name not in book.data:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    else:
        return "Contact already exists."

@input_error
def change_contact(args, book):
    name, phone = args
    if name in book.data:
        book.data[name].remove_phone(phone)
        book.data[name].add_phone(phone)
        return "Contact updated."
    else:
        return "Contact not found."

def show_phone(args, book):
    name = args[0]
    if name in book.data:
        return f"Phone: {'; '.join(str(p.value) for p in book.data[name].phones)}"
    else:
        return "Contact not found."

def show_all(book):
    if book:
        return "\n".join(str(record) for record in book.data.values())
    else:
        return "No contacts in the address book."

@input_error
def add_birthday(args, book):
    name, birthday = args
    if name in book.data:
        book.data[name].add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

def show_birthday(args, book):
    name = args[0]
    if name in book.data and book.data[name].birthday:
        return f"Birthday: {book.data[name].birthday.value}"
    elif name in book.data:
        return "Birthday not set."
    else:
        return "Contact not found."

def birthdays(book):
    upcoming_birthdays = []
    current_day = datetime.now().date()
    next_week = current_day + timedelta(days=7)

    for record in book.data.values():
        if record.birthday:
            birthday_datetime = record.birthday.as_datetime().date()
            birthday_this_year = datetime(current_day.year, birthday_datetime.month, birthday_datetime.day).date()

            if birthday_this_year < current_day:
                birthday_this_year = datetime(current_day.year + 1, birthday_datetime.month, birthday_datetime.day).date()

            days_till_birthday = (birthday_this_year - current_day).days

            if 0 <= days_till_birthday <= 7:
                upcoming_birthdays.append({"name": record.name.value, "birthday": birthday_this_year.strftime("%d.%m.%Y")})

    return upcoming_birthdays

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        return pickle.dump(book, file)
    
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()

if __name__ == "__main__":
    main()