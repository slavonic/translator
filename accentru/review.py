import torch
import pytorch_lightning as pl
from accentru.accentru_dataset import AccentruDataset
from accent.model import Model
import numpy as np

datamodule = AccentruDataset()
datamodule.prepare_data()
datamodule.setup()
vocab = datamodule.vocab

unvocab = { y: x for x,y in vocab.items() }

model = Model.load_from_checkpoint(
    'model-accentru.ckpt',
    vocab_size=datamodule.vocab_size,
    max_seq_len=32,
)

model.eval()
hits = 0
miss = 0

for batch in datamodule.val_dataloader():
    in_ = batch['in']
    out = batch['out']
    lens = batch['len']
    logits = model.forward(in_, lens)

    for i in range(logits.shape[0]):
        nlogits = logits[i, :lens[i]].detach().numpy()
        nlogits = nlogits[:, 1] - nlogits[:, 0]
        prediction_index = nlogits.argmax(axis=0)
        prediction = np.zeros(lens[i], dtype=np.int32)
        prediction[prediction_index] = 1
        word = ''.join(unvocab[i] for i in in_[i].tolist()[:lens[i].item()])
        outx = out[i, :lens[i]].detach().numpy()
        if all(x==y for x, y in zip(prediction, outx)):
            hits += 1
        else:
            print(word, prediction, outx)
            miss += 1
    # break
    print(hits, miss, miss / (hits + miss))
print(hits, miss, miss / (hits + miss))

