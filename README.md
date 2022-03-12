# Word translation from civic script to Church Slavonic

https://wandb.ai/elbat/translator/reports/---VmlldzoxNjc4NDQy/edit?firstReport=&runsetFilter

## Data preparation

See data/README.md

## Training
```bash
python -m translator.train
```

## Reviewing
```bash
python -m translator.review
```
This command will use validation partition to compute the error rates. It computes
error rates on accented and unaccented input separately, and also provides overall
(balanced) error rate.

## Converting to ONNX
(and extracting vocab)

```bash
python -m translator.onnx_export
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
