# Accenting russian words (stressing)

Source of the training data is `data/stress.dict`, downloaded from http://dataset.sova.ai/SOVA-TTS/tps_data/stress.dict (see also the repo https://github.com/sovaai/sova-tts-tps.git).

## Utilities and data processing pipeline

1. Converting dictionary to a simple list of accented words.
2. Training model on converted dictionary
3. Evaluating (reviewing) the built model on validation set
4. Converting PyTorch model to ONNX format
5. Building compressed dictionary (to optimize load time)

## Converting dictionary to a simple list of accented words

Input: `data/stress.dict`
Output: `data/ru_stress.txt`
Command: `python -m accentru.convert_dict`

From the input dictionary, we drop words that
1. have less than 2 vowels (no need to set stress on a word with a single syllable)
2. have dash (words componded with dash have separate accents in each of their components)
3. contain letter "ё" (words with "ё" in most cases do not require a separate accent [but consider "трёхпа'лый"])

We also drop symbols "'" from the words in the original dictionary that seem to be a noise.

## Model training

Input: `data/ru_stress.txt`
Output: `model-accentru.ckpt`, cached dataset
Command: `python -m accentru.train`

Training runs can be reviewed on W&B: https://wandb.ai/elbat/accentru?workspace=user-pgmmpk

## Evaluating (reviewing) model performance

Input: cached dataset built from `data/ru_stress.txt`
Output: screen
Command: `python -m accentru.review`

## Converting to ONNX

Input: `model-accentru.ckpt`
Output: `model-accentru.onnx`, `vocab-accentru.json`
Command: `python -m accentru.onnx_export`

## Compressing stress dictionary

Input: `data/ru_stress.txt`
Output: `data/ru_stress_compressed.txt`
Command: `python -m accentru.compress_stress`

## Final predictor class
Class `Predictor` in `accentru.predictor` implements final code that:
1. Loads compressed stress dictionary
2. Loads ML model

At run time for the input word it will:
1. Do nothing if word contains 'ё' or has less than 2 vowels.
2. Do nothing if word contains accent character `\u0301`
3. If input word contains symbol "'", it converts it to accent and returns
4. Consult compress stress dictionary and if lowercase version of input has match, uses it to set the stress
5. Runs ML model to predict stress position
