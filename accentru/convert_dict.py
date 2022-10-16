import re

RE_VOWELS = '[уеыаоэюия]'
RE_WORD = '^[абвгдеёжзийклмнопрстуфхцчшщьыъэюя]+$'

def num_vowels(word):
    return len(re.split(RE_VOWELS, word, flags = re.IGNORECASE)) - 1


def convert_dict(in_file, out_file):
    with open(in_file, encoding='utf-8') as f:
        words = [l.strip().split('|')[1] for l in f if l.strip()]

    with open(out_file, 'w') as f:
        for word in words:
            assert word.lower() == word
            word = word.replace("'", '')
            if not re.match(RE_WORD, word.replace('+', ''), flags=re.IGNORECASE):
                print(word)
                continue
            if num_vowels(word) <= 1 or 'ё' in word:
                continue
            pieces = word.split('+')
            assert len(pieces) == 2
            accent = len(pieces[0])  # accented character index
            word = word.replace('+', '')
            word = list(word)
            word.insert(accent + 1, '\u0301')
            word = ''.join(word)
            f.write(word + '\n')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Converts stress.dict to a simple list of accented words')
    parser.add_argument('-d', '--data',  default='data/stress.dict', help='Input file - the stress dictionary')
    parser.add_argument('-o', '--out',  default='data/ru_stress.txt', help='Output file - list of accented russian words')

    args = parser.parse_args()

    convert_dict(args.data, args.out)