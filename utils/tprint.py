# Микромодуль для вывода информации на консоль с датой и временем
# by Wokashi RG
# https://github.com/wokashi-rg

from datetime import now


def current_time():
    return str(datetime.now()) + ': '


def log(*msg):
    print(current_time() + ' '.join([str(x) for x in msg]))
