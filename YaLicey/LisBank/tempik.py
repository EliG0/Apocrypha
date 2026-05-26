def check_text():
    f = open('tempfile.txt', encoding='utf-8')
    global fread
    fread = list(map(lambda x: x.rstrip('\n'), f.readlines()))
    if fread:
        return fread[0], fread[1]
    else:
        return False


def create_temp(telnum, pas=0, user=0):
    f = open('tempfile.txt', 'w', encoding='utf-8')
    f.write(f'{telnum}\n{pas if pas != 0 else ""}\n{user if user != 0 else ""}')
    f.close()


def forsuclog():
    fread = list(map(lambda x: x.rstrip('\n'), open('tempfile.txt', encoding='utf-8').readlines()))
    if len(fread) == 3:
        return fread[2]
    else:
        clear_temp()
        return fread[0]


def clear_temp():
    open('tempfile.txt', 'w', encoding='utf-8').close()
