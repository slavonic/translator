# Word translation from civic script to Church Slavonic

Web application: https://sci.ponomar.net/translate

Architecture:
* Uses large corpus of Church Slavonic texts to collect word list (with frequences)
* Words are automatically converted to civic script, preserving accents. This is the basis for conversion
  from civic to Church Slavonic. Except that sometimes different Church Slavonic forms reduce to the same
  civic form. In such a case we pick the most frequent variant of Church Slavonic form.
* Out-of-vocabulary words are converted using ML-trained interpolator (see below for the training
  instructions)

## Application requirements
Install project dependencies using PyPI.
```shell
pip install -r requirements.txt
```

## Training logs

For translator:
https://wandb.ai/elbat/translator/reports/---VmlldzoxNjc4NDQy
https://wandb.ai/elbat/translator/reports/-2022-06-29--VmlldzoyMjQ0MDM1


For accentor:
https://wandb.ai/elbat/accent/reports/Accent-training--VmlldzoyMjQwNDM4

## Data preparation

See data/README.md

## Training
```bash
python -m translator.train
python -m accent.train
```

## Reviewing
```bash
python -m translator.review
python -m accent.review
```
This command will use validation partition to compute the error rates. It computes
error rates on accented and unaccented input separately, and also provides overall
(balanced) error rate.

## Converting to ONNX
(and extracting vocab)

```bash
python -m translator.onnx_export
python -m accent.onnx_export
```
This command takes `model.ckpt` (result of training) and exports model to ONNX format
creating `model.onnx` and `vocab.json`.

ONNX model can be used with different runtimes. For example, with in-browser JS runtime.

## Web UI
Web application using the trained model is in `ui/` sub-directory.

This is a standard Svelte-based web app. Here is the development stanza:
```bash
cd ui/
npm i
npm run dev
```
