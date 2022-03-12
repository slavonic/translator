import collections


def dedup(fname='data/cu-words-civic.txt', outname='data/cu-words-civic-dedup.txt'):
    with open(fname, encoding='utf-8') as f:
        data = [l.strip().split() for l in f]
    print(f'Loaded {len(data)} samples')

    byru = collections.defaultdict(collections.Counter)
    for cu, ru, count in data:
        byru[ru].update([cu] * int(count))

    dedup = []
    for ru in byru.keys():
        cu = byru[ru].most_common(1)[0][0]
        dedup.append( (cu, ru) )

    with open(outname, 'w', encoding='utf-8') as f:
        for cu, ru in dedup:
            f.write(cu + '\t' + ru + '\n')

if __name__ == '__main__':
    dedup()
