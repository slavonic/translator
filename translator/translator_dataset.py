import os
import random

import lightning as L
import torch
import torch.utils.data


class TranslatorDataset(L.LightningDataModule):
    def __init__(self, *, fname='data/cu-words-civic-dedup.txt',
            max_len=32, batch_size=512):
        super().__init__()
        self.fname = fname
        self.max_len = max_len
        self.batch_size = batch_size
        self._cache = os.path.expanduser(r'~/.cache/translator_dataset7')

    def cache(self, name):
        return os.path.join(self._cache, name)

    def prepare_data(self):
        force = self._build_vocab()
        force = self._make_tensors(force)

    def _build_vocab(self):
        if all(os.path.isfile(x) for x in [
            self.cache('vocab.txt'),
            self.cache('train.txt'),
            self.cache('val.txt'),
        ]):
            return False

        os.makedirs(self.cache(''), exist_ok=True)

        with open(self.fname, encoding='utf-8') as f:
            dedup = [l.strip().split() for l in f]
        print(f'Loaded {len(dedup)} samples')

        random.shuffle(dedup)
        val_partition = dedup[:int(0.02 * len(dedup))]
        train_partition = dedup[len(val_partition):]

        def enrich_with_accent(partition):
            out = []
            naked_count = 0
            acc_count = 0
            for cu, ru in partition:
                ai = -1
                if '\u0301' in ru:
                    acc_count += 1
                    ai = ru.index('\u0301') - 1
                    ru = ru.replace('\u0301', '')
                    if ai >= 0:
                        out.append((cu, ru, -1))
                else:
                    naked_count += 1
                out.append((cu, ru, ai))
            print(len(out), naked_count, acc_count)
            return out

        val_partition = enrich_with_accent(val_partition)
        train_partition = enrich_with_accent(train_partition)

        charset = set()
        for cu, ru, _ in train_partition + val_partition:
            charset.update(cu)
            charset.update(ru)
        vocab = ['<pad>'] + sorted(charset)
        print(f'Vocab length: {len(vocab)}')

        with open(self.cache('vocab.txt'), 'w', encoding='utf-8') as f:
            f.write(' '.join(vocab))

        with open(self.cache('train.txt'), 'w', encoding='utf-8') as f:
            for x, y, a in train_partition:
                f.write(f'{x}\t{y}\t{a}\n')
        with open(self.cache('val.txt'), 'w', encoding='utf-8') as f:
            for x, y, a in val_partition:
                f.write(f'{x}\t{y}\t{a}\n')

        return True

    def _make_tensors(self, force=False):

        with open(self.cache('vocab.txt'), encoding='utf-8') as f:
            chars = f.read().strip().split()
        self.vocab = { c: i for i,c in enumerate(chars) }
        print(f'Loaded vocab of size {len(self.vocab)}')

        if not force and \
                os.path.isfile(self.cache('dataset_train.pth')) and \
                os.path.isfile(self.cache('dataset_val.pth')):
            return False

        with open(self.cache('train.txt'), encoding='utf-8') as f:
            train_data = [l.strip().split() for l in f]
        print(f'Loaded {len(train_data)} train samples')

        with open(self.cache('val.txt'), encoding='utf-8') as f:
            val_data = [l.strip().split() for l in f]
        print(f'Loaded {len(val_data)} val samples')

        for x, y, _ in train_data + val_data:
            if len(x) > self.max_len:
                raise RuntimeError(f'Sample too long: {x}')
            if len(y) > self.max_len:
                raise RuntimeError(f'Sample too long: {y}')

        def mk_tensors(dataset):
            dataset_cu  = torch.zeros( (len(dataset), self.max_len), dtype=torch.long)
            dataset_cu_len = torch.zeros( (len(dataset),), dtype=torch.long)
            dataset_ru  = torch.zeros( (len(dataset), self.max_len), dtype=torch.long)
            dataset_ru_acc  = torch.zeros( (len(dataset), self.max_len), dtype=torch.long)
            dataset_ru_len  = torch.zeros( (len(dataset),), dtype=torch.long)

            count = 0
            acct = 0
            for cu, ru, astr in dataset:
                ai = int(astr)
                dataset_cu_len[count] = len(cu)
                dataset_cu[count, :len(cu)] = torch.tensor([
                    self.vocab[x] for x in cu
                ], dtype=torch.long)
                dataset_ru_len[count] = len(ru)
                dataset_ru[count, :len(ru)] = torch.tensor([
                    self.vocab[x] for x in ru
                ], dtype=torch.long)
                if ai >= 0:
                    acct += 1
                    dataset_ru_acc[count, ai] = 1
                count += 1
                if count % 10_000 == 0:
                    print(count)
            print(count , acct)
            return {
                'cu': dataset_cu,
                'cu_len': dataset_cu_len,
                'ru': dataset_ru,
                'ru_acc': dataset_ru_acc,
                'ru_len': dataset_ru_len,
            }

        train = mk_tensors(train_data)
        val   = mk_tensors(val_data)

        torch.save(train, self.cache('dataset_train.pth'))
        torch.save(val, self.cache('dataset_val.pth'))

        return True

    def setup(self, stage=None):
        self.train_data = Dataset(torch.load(self.cache('dataset_train.pth')))
        self.val_data = Dataset(torch.load(self.cache('dataset_val.pth')))

    def train_dataloader(self):
        return torch.utils.data.DataLoader(self.train_data, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return torch.utils.data.DataLoader(self.val_data, batch_size=self.batch_size, shuffle=True)

    @property
    def vocab_size(self):
        return len(self.vocab)

class Dataset:
    def __init__(self, datum):
        self.ru = datum['ru']
        self.ru_acc = datum['ru_acc']
        self.cu = datum['cu']
        self.ru_len = datum['ru_len']
        self.cu_len = datum['cu_len']
        assert self.ru.shape == self.cu.shape
        assert self.cu_len.shape == self.ru_len.shape, (self.ru_len.shape, self.cu_len.shape)

    def __len__(self):
        return self.cu.shape[0]

    def __getitem__(self, i):
        return {
            'cu': self.cu[i],
            'ru': self.ru[i],
            'ru_acc': self.ru_acc[i],
            'cu_len': self.cu_len[i],
            'ru_len': self.ru_len[i],
        }


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='test-run Translator Dataset5')
    parser.add_argument('--max_len', type=int, default=32, help='max word length')
    parser.add_argument('--batch_size', type=int, default=512, help='batch size')

    args = parser.parse_args()

    data = TranslatorDataset(max_len=args.max_len, batch_size=args.batch_size)
    data.prepare_data()
    data.setup()

    count = 0
    for batch in data.train_dataloader():
        import pdb; pdb.set_trace()
        count += 1
    print(count)

    count = 0
    for batch in data.val_dataloader():
        count += 1
    print(count)