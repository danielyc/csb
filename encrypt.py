from configparser import ConfigParser
from hashlib import sha256
from base64 import b64encode, b64decode
import aes

def writeToConf(key, value, file):
    global name
    name = file
    name += ".cnf"
    config = ConfigParser()
    config.read(file)
    encValue = encr(value)
    config.set(config.sections()[0], key, encValue)
    cfgfile = open(file, 'w')
    config.write(cfgfile)
    cfgfile.close()


def readConf(key, file):
    config = ConfigParser()
    config.read(file)
    try:
        return decr(config.get(config.sections()[0], key))
    except TypeError:
        print('Password is probably incorrect')
        exit(1)


def initConf(name):
    config = ConfigParser()
    config.add_section('SupremeBotConfig')
    for x in paydetails:
        config.set('SupremeBotConfig', x, ' ')
    cfgfile = open(name, 'w')
    config.write(cfgfile)
    cfgfile.close()


def encr(value):
    m = sha256()
    m.update(password)
    key = m.digest()
    iv = m.digest()[::2]
    if len(value) == 0:
        value = ' '
    pad = 16 - len(value) % 16
    raw = value + pad * chr(pad)
    cipher = aes.AESModeOfOperationCFB(key, iv = iv)
    return b64encode(cipher.encrypt(raw)).decode('utf-8')


def decr(value):
    m = sha256()
    m.update(password)
    passwd = m.digest()
    iv = m.digest()[::2]
    cipher = aes.AESModeOfOperationCFB(passwd, iv = iv)
    decrypted = cipher.decrypt(b64decode(value))
    try:
        return decrypted[:-ord(decrypted[-1:])].decode('utf-8')
    except UnicodeDecodeError:
        print('Password is probably incorrect')
        exit(1)

def update(pd):
    old = []
    config = ConfigParser()
    config.read('config.cnf')
    if config.items(config.sections()[0])[-1][0] == 'cardtype':
        newconf = ConfigParser()
        newconf.add_section('SupremeBotConfig')
        old = config.items(config.sections()[0])
        for x in pd:
            for y in old:
                if y[0] in x.lower():
                    pd[x] = y[1]
                    newconf.set(config.sections()[0], x, y[1])
    
        cfgfile = open(name, 'w')
        newconf.write(cfgfile)
        cfgfile.close()
