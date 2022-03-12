import torch
import pytorch_lightning as pl
from translator.translator_dataset import TranslatorDataset
from translator.model import Model
import onnx
import json
import onnxruntime as ort
import numpy as np
from pyctcdecode import build_ctcdecoder


datamodule = TranslatorDataset()
datamodule.prepare_data()
datamodule.setup()

vocab = datamodule.vocab

def to_onnx(model_checkpoint='model.ckpt', onnx_filename='model.onnx'):

    model = Model.load_from_checkpoint(
        model_checkpoint    ,
        vocab_size=datamodule.vocab_size,
        max_seq_len=32,
    )

    model.eval()

    inputs = torch.zeros((1, 32), dtype=torch.int32)
    accents = torch.zeros((1, 32), dtype=torch.int32)
    torch.onnx.export(
        model,
        (inputs, accents),
        onnx_filename,

        export_params=True,        # store the trained parameter weights inside the model file
        opset_version=9,          # the ONNX version to export the model to
        do_constant_folding=True,
        input_names = ('inputs', 'accents'),
        output_names = ('logits',),
        dynamic_axes = {
            'inputs' : { 0: 'batch_size' },
            'accents': { 0: 'batch_size' },
            'logits' : { 0: 'batch_size' },
        }
    )

    with open('vocab.json', 'w') as f:
        json.dump(vocab, f)

    # Load the ONNX model
    onnx_model = onnx.load('model.onnx')

    # Check that the model is well formed
    onnx.checker.check_model(onnx_model)

    # Print a human readable representation of the graph
    print(onnx.helper.printable_graph(onnx_model.graph))

    torch_logits = model(inputs, accents)
    print(torch_logits)

def sample(onnx_model, words=['лепота', 'несть']):

    session = ort.InferenceSession('model.onnx')

    logits = session.run(None, {
        'inputs': inputs.numpy(),
        'accents': accents.numpy(),
    })

    inputs = np.zeros((len(words), 32), dtype=np.int32)
    accents = np.zeros((len(words), 32), dtype=np.int32)
    for i,word in enumerate(words):
        for j,c in enumerate(word):
            inputs[i, j] = vocab[c]

    logits = session.run(None, {
        'inputs': inputs,
        'accents': accents,
    })[0]

    # specify alphabet labels as they appear in logits
    labels = list(vocab.keys())
    assert labels[0] == '<pad>'
    labels[0] = ''

    # prepare decoder and decode logits via shallow fusion
    decoder = build_ctcdecoder(
        labels,
        # kenlm_model,
        # alpha=0.5,  # tuned on a val set
        # beta=1.0,  # tuned on a val set
    )

    for l,word in zip(logits, words):
        out = decoder.decode_beams(l)
        print(word)
        print(out)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Converts model to ONNX')
    parser.add_argument('-i', '--input', default='model.ckpt', help='Input file with Lightning checkpoint')
    parser.add_argument('-o', '--output', default='model.onnx', help='File name of the output ONNX file')

    args = parser.parse_args()

    to_onnx(args.input, args.output)