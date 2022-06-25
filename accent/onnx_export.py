import torch
import pytorch_lightning as pl
from accent.accent_dataset import AccentDataset
from accent.model import Model
import onnx
import json
import onnxruntime as ort
import numpy as np

datamodule = AccentDataset()
datamodule.prepare_data()
datamodule.setup()

vocab = datamodule.vocab

def to_onnx(model_checkpoint='model-accent.ckpt', onnx_filename='model.onnx'):

    model = Model.load_from_checkpoint(
        model_checkpoint    ,
        vocab_size=datamodule.vocab_size,
        max_seq_len=32,
    )

    model.eval()

    inputs = torch.zeros((1, 32), dtype=torch.int32)
    torch.onnx.export(
        model,
        (inputs,),
        onnx_filename,

        export_params=True,        # store the trained parameter weights inside the model file
        opset_version=9,          # the ONNX version to export the model to
        do_constant_folding=True,
        input_names = ('inputs',),
        output_names = ('logits',),
        dynamic_axes = {
            'inputs' : { 0: 'batch_size' },
            'logits' : { 0: 'batch_size' },
        }
    )

    with open('vocab-accent.json', 'w') as f:
        json.dump(vocab, f)

    # Load the ONNX model
    onnx_model = onnx.load('model-accent.onnx')

    # Check that the model is well formed
    onnx.checker.check_model(onnx_model)

    # Print a human readable representation of the graph
    print(onnx.helper.printable_graph(onnx_model.graph))

    torch_logits = model(inputs)
    print(torch_logits)

def sample(onnx_model, words=['лепота', 'несть']):

    session = ort.InferenceSession(onnx_model)

    inputs = np.zeros((len(words), 32), dtype=np.int32)
    for i,word in enumerate(words):
        for j,c in enumerate(word):
            inputs[i, j] = vocab[c]

    logits = session.run(None, {
        'inputs': inputs,
    })[0]

    # specify alphabet labels as they appear in logits
    labels = list(vocab.keys())
    assert labels[0] == '<pad>'
    labels[0] = ''

    for l,word in zip(logits, words):
        for i,a in enumerate(l):
            if a[1] > a[0]:
                accent = i
                break
        else:
            accent = -1

        if 0 <= accent < len(word):
            word = list(word)
            word.insert(accent, '\u0301')
            word = ''.join(word)

        print(word)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Converts model to ONNX')
    parser.add_argument('-i', '--input', default='model-accent.ckpt', help='Input file with Lightning checkpoint')
    parser.add_argument('-o', '--output', default='model-accent.onnx', help='File name of the output ONNX file')

    args = parser.parse_args()

    to_onnx(args.input, args.output)

    sample('model-accent.onnx')