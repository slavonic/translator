import re
import collections

CU_CHARS = '-\u0300\u0301\u0308\u0311\u033e\u0400\u0404\u0405\u0406\u040d\u0410\u0411\u0412\u0413\u0414\u0415\u0416\u0417\u0418\u0419\u041a\u041b\u041c\u041d\u041e\u041f\u0420\u0421\u0422\u0423\u0424\u0425\u0426\u0427\u0428\u0429\u042a\u042b\u042c\u042d\u042e\u042f\u0430\u0431\u0432\u0433\u0434\u0435\u0436\u0437\u0438\u0439\u043a\u043b\u043c\u043d\u043e\u043f\u0440\u0441\u0442\u0443\u0444\u0445\u0446\u0447\u0448\u0449\u044a\u044b\u044c\u044d\u044e\u044f\u0450\u0454\u0455\u0456\u0457\u045d\u0460\u0461\u0462\u0463\u0466\u0467\u046a\u046b\u046e\u046f\u0470\u0471\u0472\u0473\u0474\u0475\u0476\u0477\u047a\u047b\u047c\u047d\u047e\u047f\u0482\u0483\u0486\u0487\u1c81\u1c82\u2020\u2de0\u2de1\u2de2\u2de3\u2de4\u2de6\u2de7\u2de8\u2de9\u2dea\u2dec\u2ded\u2def\u2df1\u2df4\ua64a\ua64b\ua656\ua657\ua673\ua67e'
CU_CHARS = set(CU_CHARS)

C_EROK = '\u033e'
C_GRAVE = '\u0300'
C_ACUTE = '\u0301'
C_DIAERESIS = '\u0308'
C_CAP = '\u0311'

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create set of unique CU words')
    parser.add_argument('-i', '--input', nargs='+', default=['cu-books.txt', 'elis.txt'])
    parser.add_argument('-o', '--output', default='cu-words.txt')

    args = parser.parse_args()

    text = []
    for fname in args.input:
        with open(fname, encoding='utf-8') as f:
            text.append(f.read())
    text = '\n'.join(text)

    print(f'Loaded {len(text)} characters')

    # remove punctuation
    text = re.sub(r'[!"\(\)\*,\.:;\[\]«»꙾]+', ' ', text)
    # remove holiday parks and asterisk
    text = re.sub(r'[🕅🕂🕃🕀🕁꙳]', ' ', text)
    # remove occasional digits
    text = re.sub(r'\d+', ' ', text)
    # remove roman numerals, if any
    text = re.sub(r'(III|II|I)', ' ', text)
    # remove words that start with dash (weird)
    text = re.sub(r'\-.*?\s', ' ', text)

    # lowercase all
    text = text.lower()

    words = text.strip().split()

    # dedup
    counter = collections.Counter(words)

    words = sorted(counter.keys())

    # validate all words
    count = 0
    for word in words:
        count += 1
        if count % 10_000 == 0:
            print(count)
        if set(word) - CU_CHARS:
            print((''.join(set(word)-CU_CHARS)).encode('unicode-escape').decode())
            print(word, words[count-5: count+5])
            assert False

    with open(args.output, 'w', encoding='utf-8') as f:
        for word, count in sorted(counter.items()):
            f.write(f'{word}\t{count}\n')
    print(f'Created dataset of {len(words)} words.')
