from werkzeug.security import check_password_hash, generate_password_hash


def geneate_pwd(pwd):
    return generate_password_hash(pwd)


def check_pwd(x, y):
    return check_password_hash(y, x)
