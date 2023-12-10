from collections import UserDict
from datetime import datetime
import json


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self):
        return str(self.value)
    
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Name(Field):
    pass


class Birthday(Field):
    @Field.value.setter
    def value(self, value: str):
        try:
            self._Field__value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid birthday format. Use YYYY-MM-DD")


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @Field.value.setter
    def value(self, value):
        if value.isdigit() and len(value) == 10:
            self._Field__value = value
        else:
            raise ValueError ("Invalid phone number format. Phone not added.")
    

class Record:
    def __init__(self, name, birthday = None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if not any(p.value == old_phone for p in self.phones):
            raise ValueError("Phone number not found.")
        
        self.remove_phone(old_phone)
        self.add_phone(new_phone)
        
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def days_to_birthday(self):
        if not self.birthday:
            return None
        
        today = datetime.today()
        next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)

        if today > next_birthday:
            next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)

        days_left = (next_birthday - today).days
        return days_left


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, query):
        results = []
        for name, record in self.data.items():
            if query.lower() in name.lower():
                results.append(record)
            else:
                for phone in record.phones:
                    if query in phone.value:
                        results.append(record)
                        break
        return results

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, item_number):
        counter = 0
        result = ''
        for item, record in self.data.items():
            result += f'{item}: {record}'
            counter += 1
            if counter >= item_number:
                yield result
                counter = 0
                result = ''

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            data_to_save = {
                'records': {name: {'phones': [phone.value for phone in record.phones],
                                   'birthday': str(record.birthday.value) if record.birthday else None}
                            for name, record in self.data.items()}
            }
            json.dump(data_to_save, file)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            for name, record_data in data['records'].items():
                record = Record(name, birthday=record_data['birthday'])
                for phone in record_data['phones']:
                    record.add_phone(phone)
                self.add_record(record)

    def add_contact(address_book):
        name = input("Enter contact name: ")
        birthday = input("Enter birthday (YYYY-MM-DD): ")
        record = Record(name, birthday)
    
        phone_count = input("Enter the number of phone numbers to add: ")
        record.add_phone(phone_count)
    
        address_book.add_record(record)
        print("Contact added successfully.")

    def delete_contact(address_book):
        name = input("Enter contact name to delete: ")
        address_book.delete(name)
        print("Contact deleted successfully.")

    def search_contacts(address_book):
        query = input("Enter name or phone number to search: ")
        results = address_book.find(query)
    
        if results:
            print("Search results:")
            for result in results:
                print(result)
        else:
            print("No matching contacts found.")

    def show_all_contacts(self):
        if self.data:
            print("\nAll contacts:")
            for record in self.data.values():
                print(record)

    def show_all_contacts_with_birthdays(address_book):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in address_book.values():
            days_left = record.days_to_birthday()
            if days_left is not None:  
                upcoming_birthdays.append((record, days_left))

        if upcoming_birthdays:
            print("\nUpcoming birthdays:")
            for record, days_left in upcoming_birthdays:
                print(f"{record.name.value}: {record.birthday.value} (in {days_left} days)")

def main():
    address_book = AddressBook()

    # Відновлення даних з файлу при запуску програми
    try:
        address_book.load_from_file('address_book.json')
        print("Address book loaded successfully.")
    except FileNotFoundError:
        print("No existing address book found.")

    while True:
        print("\nOptions:")
        print("1. Add contact")
        print("2. Delete contact")
        print("3. Search contacts")
        print("4. Show all contacts")
        print("5. Contacts birthday")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            address_book.add_contact()
        elif choice == '2':
            address_book.delete_contact()
        elif choice == '3':
            address_book.search_contacts()
        elif choice == '4':
            address_book.show_all_contacts()
        elif choice == '5':
            address_book.show_all_contacts_with_birthdays()
        elif choice == '6':
            address_book.save_to_file('address_book.json')
            print("Address book saved. Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()