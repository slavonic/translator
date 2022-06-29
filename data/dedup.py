import collections


def dedup(fname='cu-words-civic.txt', outname='cu-words-civic-dedup.txt'):
    with open(fname, encoding='utf-8') as f:
        data = [l.strip().split() for l in f]
    print(f'Loaded {len(data)} samples')

    byru = collections.defaultdict(collections.Counter)
    for cu, ru, count in data:
        byru[ru].update([cu] * int(count))

    dedup = []
    for ru in byru.keys():
        cu, freq = byru[ru].most_common(1)[0]
        dedup.append( (cu, ru, freq) )

    with open(outname, 'w', encoding='utf-8') as f:
        for cu, ru, freq in dedup:
            f.write(f'{cu}\t{ru}\t{freq}\n')

if __name__ == '__main__':
    dedup()
