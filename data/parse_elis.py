'''
Script that parses Elisabeth Bible from

    https://github.com/typiconman/ponomar/tree/master/Ponomar/languages/cu/bible/elis

and extracts pure text:

1. Lines preserved
2. Verse numbers removed.
3. One sentence per line.
4. Books separated by \n\n
'''
import glob
import os
import re

def xml2text(x):
    x = re.sub('<\\?xml .*?>', '', x)
    x = re.sub('<document .*?>', '', x)
    x = re.sub('</document>', '[PAR]', x)
    x = re.sub('<footer>', '', x)
    x = re.sub('</footer>', '[PAR]', x)
    x = re.sub('<footer/>', '[PAR]', x)
    x = re.sub('<p.*?>', '', x)
    x = re.sub('</p>', '[PAR]', x)
    x = re.sub('<red>', '', x)
    x = re.sub('</red>', '', x)
    x = re.sub('<anchor .*?>', '', x)
    x = re.sub('<footnote.*?>', ' ', x)
    x = re.sub('</footnote>', '[PAR]', x)
    x = re.sub('<disp .*?>', '', x)
    x = re.sub('</disp>', '', x)
    x = re.sub('<wide>', '', x)
    x = re.sub('</wide>', '', x)
    x = re.sub('<small>', '', x)
    x = re.sub('</small>', '', x)
    x = re.sub('<!--.*?-->', '', x)
    x = re.sub('<img .*?>', '', x)
    x = re.sub('\x8d', '', x)
    x = re.sub('\x80', '', x)
    x = re.sub('\x94', '', x)
    x = re.sub('\u2011', '-', x)

    x = re.sub(r'\s+', ' ', x)
    x = x.replace('[PAR]', '\n')
    x = re.sub(r'\s*\n\s+', '\n', x).strip()

    mtc = re.search(r'[&<>]', x)
    if mtc:
        s = max(0, mtc.start() - 20)
        raise RuntimeError(x[s:mtc.end() + 100])

    return x

def clean_markup(line):
    # remove Зачало
    line = re.sub(r'\*\*\(.*?\)\*\*', '', line)
    line = re.sub(r'\*\*\s+Composite\s.*?\*\*', '', line)
    line = re.sub(r'жи\[ша\]с', 'жишас', line)
    line = re.sub(r'\s\[же\]\s', ' ', line)
    line = re.sub(r'\[и҆\]', 'и҆', line)
    line = re.sub(r'\[(Быт|И҆с|При́тч|г҃ ца́р|д́҃ ца́р|И҆сх|Чи́с|Леѵ|Мал|Мк|Матѳ|Лк|І҆ѡа́н)\s\d+:\d+\]', '', line)
    line = re.sub(r'{(.*?)}', '(\\1)', line)
    line = re.sub(r'\(βάτους, т. є҆. мѣ́ръ\)', ' ', line)
    assert '**' not in line, line
    assert '[' not in line, line
    assert ']' not in line, line
    assert '{' not in line, line
    assert '}' not in line, line
    assert '/' not in line, line
    assert '\\' not in line, line
    line = re.sub(r'\s+', ' ', line).strip()
    return line

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('Parses cu-books')
    parser.add_argument('-r', '--root', default=os.path.expanduser(r'~/git/ponomar/Ponomar/languages/cu/bible/elis'))
    parser.add_argument('-o', '--output', default='elis.txt')

    args = parser.parse_args()

    exceptions = {
        'Коне́цъ кни́зѣ пе́рвѣй мѡѷсе́овѣ: и҆́мать въ себѣ̀ гла́въ 50',
    }

    text = []
    for book in glob.glob(args.root + '/*.text'):
        print(f'Processing {book}')
        with open(book, encoding='utf-8') as f:
            lineno = 0
            for line in f:
                lineno += 1
                line = line.strip()
                if line == '':
                    text.append('\n')
                elif re.match(r'^.?#\d+$', line):
                    text.append('\n')
                elif mtc := re.match(r'\d+\|\s*', line):
                    text.append(clean_markup(line[mtc.end():]))
                elif line in exceptions:
                    text.append(line)
                else:
                    assert False, (book, lineno, line)
            text.append('\n')

    text = (' '.join(text)).strip()
    text = re.sub('\s*\n\s*', '\n', text)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(text + '\n')
    print(f'Saved elis corpus, {len(text)} characters')
