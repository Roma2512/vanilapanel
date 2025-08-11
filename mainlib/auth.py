import uuid

Tokens = []
def authsession(token):
    if token in Tokens:
        return True
    else:
        return False
def loginuser(username, password):
    if username == "admin" and password == "mgnd3mngn4ndn6n":
        token = str(uuid.uuid4())
        Tokens.append(token)
        return {"code": True, "token": token}
    else:
        return {"code": False, "message": "Неверный логин или пароль"}