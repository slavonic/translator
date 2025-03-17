import collections


def accent(
    fname='cu-words-civic-dedup.txt',
    outname='cu-words-civic-dedup-accent.txt',
    addendum='accent-addendum.txt'
):
    with open(fname, encoding='utf-8') as f:
        data = [l.strip().split() for l in f]
    print(f'Loaded {len(data)} samples')

    byru = collections.defaultdict(collections.Counter)
    for _, ru, count in data:
        byru[ru.replace('\u0301', '')].update([ru] * int(count))

    with open(addendum, encoding='utf-8') as f:
        addendum = [l.strip().split('|') for l in f]
    print(f'..and {len(addendum)} addenda')
    for _, w in addendum:
        index = w.index('+')
        assert index >= 0
        w = w.replace('+', '')
        if w in byru:
            print('WARNING, addendum overwites corpus item (or duplicate addendum word)! Fix corpus instead:', w)
            continue
        w = w[:index+1] + '\u0301' + w[index+1:]
        byru[w.replace('\u0301', '')].update([w])

    dedup = []
    for ru in byru.keys():
        nk, freq = byru[ru].most_common(1)[0]
        dedup.append( (ru, nk, freq) )

    with open(outname, 'w', encoding='utf-8') as f:
        for ru, nk, freq in sorted(dedup):
            f.write(f'{ru}\t{nk}\t{freq}\n')

if __name__ == '__main__':
    accent()
