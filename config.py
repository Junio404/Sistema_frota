import os
import random
import string

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
random_str = string.ascii_letters + string.digits + string.ascii_uppercase
key = ''.join(random.choice(random_str) for i in range(12))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or key
    DATABASE = os.path.join(BASE_DIR, "meu_banco.db")
    DEBUG = True