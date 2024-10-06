def check_login(login):
    return len(login) >= 6 and all('A' <= char <= 'Z' or 'a' <= char <= 'z' or '0' <= char <= '9' for char in login)

def check_password(password):
    if len(password) < 6:
        return False

    has_lower = has_upper = has_digit = False

    for char in password:
        if 'a' <= char <= 'z':
            has_lower = True
        elif 'A' <= char <= 'Z':
            has_upper = True
        elif '0' <= char <= '9':
            has_digit = True
        elif 'А' <= char <= 'Я' or 'а' <= char <= 'я':
            return False

    return has_lower and has_upper and has_digit
