#Main class for User
from flask_login import UserMixin
class User(UserMixin):
    def __init__(self,username,password) -> None:
       self.username=username
       self.password=password
       self._authenticated=False

    def is_authenticated(self):
        return self._authenticated

    def get_id(self):
        return self.username

    
        