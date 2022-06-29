import argparse

parser = argparse.ArgumentParser(description='Validates civic forms')
parser.add_argument('-i', '--input', default='cu-words-civic.txt', help='Input file')

args = parser.parse_args()

import collections

VOWELS = 'аеиоуыэюя'

stats = collections.defaultdict(int)
with open(args.input, encoding='utf-8') as f:
    for line in f:
        word = line.strip().split()[1]
        num_accents = len([x for x in word if x == '\u0301'])
        num_vowels = len([x for x in word if x in VOWELS])
        if num_accents != 1 and num_vowels > 1:
            stats[num_accents] += 1
            print(word)

print(stats)