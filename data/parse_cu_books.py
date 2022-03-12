'''
Script that parses XML from 

    https://github.com/slavonic/cu-books

and extracts pure text:

1. All XML markup is removed.
2. Blocks (paragraphs, headings, etc) separated by \n
3. Books separated by \n\n
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
    x = re.sub('<footnote lang="(ru|cu|bg|de|el)">.*?</footnote>', '', x, flags=re.DOTALL | re.MULTILINE)
    x = re.sub('<footnote.*?>', ' ', x)
    x = re.sub('</footnote>', '[PAR]', x)
    x = re.sub('<disp lang="(ru|cu|bg|de|el)">.*?</disp>', '', x, flags=re.DOTALL | re.MULTILINE)
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
    x = re.sub('Свято-Успенский Псково-Печерский монастырь. Издательский отдел Московского Патриархата Опущены при оцифровке тексты чинов: малой вечерни, великой вечерни, бденной, полиелейной, шестеричной служб, утрени без бдения. Найти можно в Типиконе.', '[PAR]', x)
    x = re.sub('Свято-Троицкая Сергиева Лавра 1995', '[PAR]', x)
    x = re.sub('Репринт издания: Москва Синодальная типография 1913', '[PAR]', x)
    x = re.sub('сохранена орфография оригинала', '[PAR]', x)
    x = re.sub('София, 1948', '[PAR]', x)
    x = re.sub('Свято-Успенский Псково-Печерский монастырь. Издательский отдел Московского Патриархата', '[PAR]', x)
    x=  re.sub('По благословению Святейшего Патриарха Московского и Всея Руси Алексия ІІ', '[PAR]', x)
    x = re.sub('По благословению Святейшего Патриарха Московского и всея Руси', '[PAR]', x)
    x = re.sub('Издательский отдел Московской Патриархии при участии издательско-информационного агенства «Голос», 103031, Москва, ул. Петровка, д. 11/20.', '[PAR]', x)
    x = re.sub('Отпечатано с оригинал-макета на Можайском полиграфкомбинате Министерства печати и информации Российской Федерации, 143200, г. Можайск, ул. Мира, 93.', '[PAR]', x)
    x = re.sub('Заказ 1189, Тираж 30000 Экз.', '[PAR]', x)
    x = re.sub('Московский Сретенский монастырь, издательство «Правило веры», 1996', '[PAR]', x, flags=re.MULTILINE)
    x = re.sub('Московский Сретенский монастырь, издательство «Правило веры», 1997', '[PAR]', x, flags=re.MULTILINE)
    x = re.sub('Издание Московской Патриархии', '[PAR]', x)
    x = re.sub('ИЗДАНИЕ МОСКОВСКОЙ ПАТРИАРХИИ МОСКВА 1992', '[PAR]', x)
    x = re.sub('Издание Московской Патриархии', '[PAR]', x)
    x = re.sub('ИЗДАНИЕ МОСКОВСКОЙ ПАТРИАРХИИ', '[PAR]', x)
    x = re.sub('МОСКВА 1992', '[PAR]', x)
    x = re.sub(r'\[с\. 273\]', '', x)
    x = re.sub(r'\(12\)', ' ', x)
    x = re.sub(r'стр.\s*\d+', ' ', x, flags=re.IGNORECASE)

    x = re.sub(r'\?', '', x)
    x = re.sub('_', ' ', x)

    x = re.sub(r'\s+', ' ', x)
    x = x.replace('[PAR]', '\n')
    x = re.sub(r'\s*\n\s+', '\n', x).strip()

    mtc = re.search(r'[&<>]', x)
    if mtc:
        s = max(0, mtc.start() - 20)
        raise RuntimeError(x[s:mtc.end() + 100])

    return x

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('Parses cu-books')
    parser.add_argument('-r', '--root', default=os.path.expanduser(r'~/git/cu-books'))
    parser.add_argument('-o', '--output', default='cu-books.txt')

    args = parser.parse_args()

    text = []
    for book in glob.glob(args.root + '/*'):
        if os.path.basename(book) in ('LICENSE', 'util', 'Makefile', 'README.md', 'package-lock.json'):
            continue
        print(f'Processing {book}')
        assert os.path.isdir(book + '/chapters'), book
        for chapter in glob.glob(book + '/chapters/*'):
            assert chapter.endswith('.xml'), chapter
            with open(chapter, encoding='utf-8') as f:
                t = xml2text(f.read())
            text.append(t)

    text = '\n\n'.join(text)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(text + '\n')
    print(f'Saved cu-books corpus, {len(text)} characters')
