import collections


def accent(fname='cu-words-civic-dedup.txt', outname='cu-words-civic-dedup-accent.txt'):
    with open(fname, encoding='utf-8') as f:
        data = [l.strip().split() for l in f]
    print(f'Loaded {len(data)} samples')

    byru = collections.defaultdict(collections.Counter)
    for _, ru, count in data:
        byru[ru.replace('\u0301', '')].update([ru] * int(count))

    dedup = []
    for ru in byru.keys():
        nk, freq = byru[ru].most_common(1)[0]
        dedup.append( (ru, nk, freq) )

    with open(outname, 'w', encoding='utf-8') as f:
        for ru, nk, freq in sorted(dedup):
            f.write(f'{ru}\t{nk}\t{freq}\n')

if __name__ == '__main__':
    accent()
