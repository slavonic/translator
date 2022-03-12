import torch
import pytorch_lightning as pl
from translator.translator_dataset import TranslatorDataset
from translator.model import Model

datamodule = TranslatorDataset()
datamodule.prepare_data()
datamodule.setup()
vocab = datamodule.vocab

unvocab = { y: x for x,y in vocab.items() }

model = Model.load_from_checkpoint(
    'model.ckpt',
    vocab_size=datamodule.vocab_size,
    max_seq_len=32,
)


from pyctcdecode import build_ctcdecoder

# specify alphabet labels as they appear in logits
labels = list(datamodule.vocab.keys())

# prepare decoder and decode logits via shallow fusion
decoder = build_ctcdecoder(
    list('' if x == '<pad>' else x for x in datamodule.vocab.keys()),
    # kenlm_model,
    # alpha=0.5,  # tuned on a val set
    # beta=1.0,  # tuned on a val set
)

unvocab = { b: a for a,b in datamodule.vocab.items() }

model.eval()
hits = 0
miss = 0
hits_unhinted = 0
hits_hinted = 0
miss_unhinted = 0
miss_hinted = 0
for batch in datamodule.val_dataloader():
    ru = batch['ru']
    ru_acc = batch['ru_acc']
    logits = model.forward(ru, ru_acc, batch['ru_len'])

    cu = batch['cu']
    cu_len = batch['cu_len']
    ru = batch['ru']
    ru_len = batch['ru_len']

    for i in range(logits.shape[0]):
        nlogits = logits[i].detach().numpy()
        text = decoder.decode(nlogits)
        truth = ''.join(unvocab[i] for i in cu[i].tolist()[:cu_len[i].item()])
        inp   = ''.join(unvocab[i] for i in ru[i].tolist()[:ru_len[i].item()])
        has_accent = ru_acc[i].sum().detach().item() > 0
        if text == truth:
            if has_accent:
                hits_hinted += 1
            else:
                hits_unhinted += 1
            hits += 1
        else:
            if has_accent:
                miss_hinted += 1
            else:
                miss_unhinted += 1
            print(inp, has_accent, text, truth)
            miss += 1
    # break
    print(hits, miss, miss / (hits + miss))
    print('\t', miss_unhinted / (hits_unhinted + miss_unhinted + 1.e-6))
    print('\t', miss_hinted / (hits_hinted + miss_hinted + 1.e-6))
print(hits, miss, miss / (hits + miss))
print('\t', miss_unhinted / (hits_unhinted + miss_unhinted + 1.e-6))
print('\t', miss_hinted / (hits_hinted + miss_hinted + 1.e-6))

