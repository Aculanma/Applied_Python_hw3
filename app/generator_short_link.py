import random
import string

# генерируем строку длины 5, состоящих из цифр и букв
def generate_short_code(length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))