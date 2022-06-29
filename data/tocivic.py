import re
import collections
import unicodedata

CU_CHARS = '-\u0300\u0301\u0308\u0311\u033e\u0400\u0404\u0405\u0406\u040d\u0410\u0411\u0412\u0413\u0414\u0415\u0416\u0417\u0418\u0419\u041a\u041b\u041c\u041d\u041e\u041f\u0420\u0421\u0422\u0423\u0424\u0425\u0426\u0427\u0428\u0429\u042a\u042b\u042c\u042d\u042e\u042f\u0430\u0431\u0432\u0433\u0434\u0435\u0436\u0437\u0438\u0439\u043a\u043b\u043c\u043d\u043e\u043f\u0440\u0441\u0442\u0443\u0444\u0445\u0446\u0447\u0448\u0449\u044a\u044b\u044c\u044d\u044e\u044f\u0450\u0454\u0455\u0456\u0457\u045d\u0460\u0461\u0462\u0463\u0466\u0467\u046a\u046b\u046e\u046f\u0470\u0471\u0472\u0473\u0474\u0475\u0476\u0477\u047a\u047b\u047c\u047d\u047e\u047f\u0482\u0483\u0486\u0487\u1c81\u1c82\u2020\u2de0\u2de1\u2de2\u2de3\u2de4\u2de6\u2de7\u2de8\u2de9\u2dea\u2dec\u2ded\u2def\u2df1\u2df4\ua64a\ua64b\ua656\ua657\ua673\ua67e'
CU_CHARS = set(CU_CHARS)

C_EROK = '\u033e'
C_GRAVE = '\u0300'
C_ACUTE = '\u0301'
C_DIAERESIS = '\u0308'
C_PNEUMATA = '\u0486'
C_CAP = '\u0311'

TITLO = '\u0483'

ALLOWED = '\u0301абвгдежзийклмнопрстуфхцчшщьыъэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ-'
ALLOWED = set(ALLOWED)

VOWELS = 'аеиоуыэюя'

MAP = {
    'ѧ': 'я',
    'ѣ': 'е',
    'Ѧ': 'Я',
    'І': 'И',
    'ꙋ': 'у',
    'ѿ': 'от',
    'Ѽ': 'О',
    'ѽ': 'о',
    'і': 'и',
    'ꙗ': 'я',
    'є': 'е',
    'ѱ': 'пс',
    'ѻ': 'о',
    'Є': 'Е',
    'Ꙗ': 'Я',
    'Ѡ': 'О',
    'ѕ': 'з',
    'Ѳ': 'Ф',
    'Ѿ': 'От',
    'Ѻ': 'О',
    'ѷ': 'и',
    'Ѕ': 'З',
    'Ѱ': 'Пс',
    'Ѣ': 'Е',
    'Ꙋ': 'У',
    'Ѵ': 'В',
    'ѯ': 'кс',
    C_EROK: 'ъ',
    'ѡ': 'о',
    'ї': 'и',
    'ѳ': 'ф',
}

DIGITS = {
    '' : 0,
    'а': 1,
    'в': 2,
    'г': 3,
    'д': 4,
    'є': 5,
    'є': 5,
    'ѕ': 6,
    'з': 7,
    'и': 8,
    'ѳ': 9,
    'і': 10,
    'к': 20,
    'л': 30,
    'м': 40,
    'н': 50,
    'ѯ': 60,
    'о': 70,
    'ѻ': 70,
    'п': 80,
    'ч': 90,
    'р': 100,
    'с': 200,
    'т': 300,
    'у': 400,
    'ф': 500,
    'х': 600,
    'ѱ': 700,
    'ѿ': 800,
    'ц': 900,
}

DD = set(DIGITS.keys())
DD.add('\u0483')
DD.add('҂')

def maybe_digit(word):
    if TITLO in word:
        pieces = word.split('-')
        if len(pieces[0]) > 0 and all(x in DD for x in pieces[0]):
            return True
    return False


EXCEPTIONS = {
    # 'аллилꙋїа': 'аллилу́иа',
    # 'аминь': 'ам\u0301инь',
    # 'апостола': 'ап\u0301остола',
    # 'архїерей': 'архиере\u0301й',
    # 'архїереовꙋ': 'архиере\u0301ову',
    # 'аще': 'а\u0301ще',
    # 'без̾именитое': 'безъимени\u0301тое',
}

def tocivic(word):
    if maybe_digit(word):
        return None
    if word in { '†' }:
        return None
    if word in EXCEPTIONS:
        return EXCEPTIONS[word]
    word = unicodedata.normalize('NFD', word)
    if word[0] == 'ѿ' and C_PNEUMATA not in word:
        word = 'о' + C_PNEUMATA + 'т' + word[1:]  # synthesize pheumata

    civic = ''.join(MAP.get(x, x) for x in word)
    civic = re.sub(r'ѵ҆', 'и' + C_PNEUMATA, civic)

    if C_ACUTE in civic:
        civic = civic.replace(C_GRAVE, '').replace(C_CAP, '')
    elif C_GRAVE in civic:
        civic = civic.replace(C_CAP, '').replace(C_GRAVE, C_ACUTE)
    elif C_CAP in civic:
        civic = civic.replace(C_CAP, C_ACUTE)
    elif C_PNEUMATA in civic:
        civic = civic.replace(C_PNEUMATA, C_ACUTE)
    elif C_DIAERESIS in civic:
        civic = civic.replace(C_DIAERESIS, C_ACUTE)
    civic = civic.replace(C_PNEUMATA, '').replace(C_DIAERESIS, '')
    civic = civic.replace('\u1c82', '')
    civic = unicodedata.normalize('NFC', civic)
    civic = re.sub(r'ѵ́', 'и\u0301', civic)
    if C_ACUTE in civic:
        civic = civic.replace('ѷ', 'и')
    else:
        civic = civic.replace('ѷ', 'и\u0301')
    civic = civic.replace('ѵ', 'в')
    if civic[-1] == 'ъ':
        civic = civic[:-1]
    if len(civic) == 0:
        return None
    if len(set(civic) - ALLOWED) == 0:
        if len([c for c in civic if c in VOWELS]) < 2:
            civic = civic.replace('\u0301', '')  # need no accents in a single-vowel word
        return civic
    print(word, civic, [x.encode('unicode-escape') for x in set(civic) - ALLOWED])
    return None

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Converts to civic script')
    parser.add_argument('-i', '--input', default='cu-words-untitlo.txt')
    parser.add_argument('-o', '--output', default='cu-words-civic.txt')

    args = parser.parse_args()

    with open(args.input, encoding='utf-8') as f:
        dataset = [l.strip().split() for l in f]

    print(f'Loaded {len(dataset)} words')

    with open(args.output, 'w', encoding='utf-8') as f:
        counter = 0
        for word, expanded, count in dataset:
            counter += 1
            if counter % 1000 == 0:
                print(counter)
            converted = tocivic(expanded)
            if converted is not None:
                f.write(f'{word}\t{converted}\t{count}\n')
