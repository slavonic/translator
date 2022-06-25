import pytorch_lightning as pl
import torch
import torch.utils.data
import torch.nn.functional as F
import os
import random
import re
import collections


class AccentDataset(pl.LightningDataModule):
    def __init__(self, *, fname='data/cu-words-civic-dedup.txt',
            max_len=32, batch_size=512):
        super().__init__()
        self.fname = fname
        self.max_len = max_len
        self.batch_size = batch_size
        self._cache = os.path.expanduser(r'~/.cache/accent_dataset')

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
            data = [l.strip().split()[-1] for l in f]
        print(f'Loaded {len(data)} samples')

        random.shuffle(data)
        val_partition = data[:int(0.02 * len(data))]
        train_partition = data[len(val_partition):]

        charset = set()
        for word in train_partition + val_partition:
            charset.update(word)
        charset.remove('\u0301')
        vocab = ['<pad>'] + sorted(charset)
        print(f'Vocab length: {len(vocab)}')

        with open(self.cache('vocab.txt'), 'w', encoding='utf-8') as f:
            f.write(' '.join(vocab))

        with open(self.cache('train.txt'), 'w', encoding='utf-8') as f:
            for x in train_partition:
                f.write(f'{x}\n')
        with open(self.cache('val.txt'), 'w', encoding='utf-8') as f:
            for x in val_partition:
                f.write(f'{x}\n')

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
            train_data = [l.strip() for l in f]
        print(f'Loaded {len(train_data)} train samples')

        with open(self.cache('val.txt'), encoding='utf-8') as f:
            val_data = [l.strip() for l in f]
        print(f'Loaded {len(val_data)} val samples')

        for x in train_data + val_data:
            if len(x) > self.max_len:
                raise RuntimeError(f'Sample too long: {x}')

        def mk_tensors(dataset):
            dataset_in  = torch.zeros( (len(dataset), self.max_len), dtype=torch.long)
            dataset_out  = torch.zeros( (len(dataset), self.max_len), dtype=torch.long)
            dataset_len = torch.zeros( (len(dataset),), dtype=torch.long)

            count = 0
            for word in dataset:
                if '\u0301' in word:
                    ai = word.index('\u0301') - 1
                    word = word.replace('\u0301', '')
                else:
                    ai = -1
                dataset_len[count] = len(word)
                dataset_in[count, :len(word)] = torch.tensor([
                    self.vocab[x] for x in word
                ], dtype=torch.long)
                if ai >= 0:
                    dataset_out[count, ai] = 1

                count += 1
                if count % 10_000 == 0:
                    print(count)
            print(count)
            return {
                'in': dataset_in,
                'out': dataset_out,
                'len': dataset_len,
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
        self.in_ = datum['in']
        self.out = datum['out']
        self.len = datum['len']

    def __len__(self):
        return self.in_.shape[0]

    def __getitem__(self, i):
        return {
            'in': self.in_[i],
            'out': self.out[i],
            'len': self.len[i],
        }


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='test-run Hyphenator Dataset5')
    parser.add_argument('--max_len', type=int, default=32, help='max word length')
    parser.add_argument('--batch_size', type=int, default=512, help='batch size')

    args = parser.parse_args()

    data = AccentDataset(max_len=args.max_len, batch_size=args.batch_size)
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