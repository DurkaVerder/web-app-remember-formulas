import re

def check_login(login):
    if re.fullmatch(r'[A-Za-z0-9]+', login):
        return True
    return False

def check_password(password):
    if (re.search(r'[a-z]', password) and
        re.search(r'[A-Z]', password) and
        re.search(r'\d', password) and
        re.fullmatch(r'[A-Za-z0-9]+', password)):
        return True
    return False


login = input()
password = input()

if check_login(login):
    print("Логин корректен")
else:
    print("Логин некорректен")

if check_password(password):
    print("Пароль корректен")
else:
    print("Пароль некорректен")
