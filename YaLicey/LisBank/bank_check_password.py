class PasswordError(Exception):
    pass


class LengthError(PasswordError):
    pass


class LetterError(PasswordError):
    pass


class DigitError(PasswordError):
    pass


class SequenceError(PasswordError):
    pass


def check_password(password):
    try:
        keyb = [
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
            'йцукенгшщзхъ', 'фывапролджэё', 'ячсмитьбю'
        ]

        a = password

        if len(a) <= 8:
            raise LengthError

        if a.islower() or a.isupper():
            raise LetterError

        if a.isdigit():
            raise LetterError

        if a.isalpha():
            raise DigitError

        if not any([i in '1234567890' for i in a]):
            raise DigitError
        for i in keyb:
            for j in range(len(i) - 2):
                if i[j:j + 3] in a.lower():
                    raise SequenceError

        return 'ok'

    except LengthError:
        return 'LengthError'
    except LetterError:
        return 'LetterError'
    except DigitError:
        return 'DigitError'
    except SequenceError:
        return 'SequenceError'

