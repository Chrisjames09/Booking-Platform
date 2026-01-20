import uuid
from werkzeug.security import check_password_hash

class FT:
    def __init__(self, email, password, type):
        self.__id = str(uuid.uuid4())
        self.__email = email
        self.__password = password
        self.type = type

    def get_id(self):
        return self.__id

    def get_email(self):
        return self.__email

    def get_password(self):
        return self.__password

    def set_email(self, email):
        self.__email = email

    def set_password(self, password):
        self.__password = password

    def get_type(self):
        return self.type
    def set_type(self, type):
        self.type = type

    def check_password(self, password):
        print(f"PLAIN:{password} HASH:{self.__password}") #DEBUG check password
        return check_password_hash(self.__password, password)