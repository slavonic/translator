import json
import onnxruntime as ort
import re
import numpy as np

class Predictor:
    def __init__(self, onnx_model, vocab, data_dict):
        self._ml_predictor = MLPredictor(onnx_model, vocab)
        self._vocab_predictor = VocabPredictor(data_dict)

    def __call__(self, word):
        prediction = self._vocab_predictor(word)
        if prediction is None:
            prediction = self._ml_predictor(word)
        return prediction

class MLPredictor:

    def __init__(self, onnx_model, vocab):
        self._session = ort.InferenceSession(onnx_model)

        with open(vocab) as f:
            self._vocab = json.load(f)

    def __call__(self, word):
        word_lower = word.lower()
        inputs = np.zeros((1, 32), dtype=np.int32)
        for j,c in enumerate(word[:32]):
            inputs[0, j] = self._vocab[c.lower()]
        logits = self._session.run(None, {
            'inputs': inputs,
        })[0][0]
        accent = (logits[:len(word),1] - logits[:len(word), 0]).argmax()
        word = list(word)
        word.insert(accent + 1, '\u0301')
        word = ''.join(word)
        return word

RE_VOWELS = '[уеыаоэюия]'

def num_vowels(word):
    return len(re.split(RE_VOWELS, word, flags = re.IGNORECASE)) - 1

class VocabPredictor:
    def __init__(self, data_dict):
        with open(data_dict, encoding='utf-8') as f:
            words = [l.strip().split('|')[1] for l in f if l.strip()]
        self._data = {}
        for word in words:
            assert word.lower() == word
            if num_vowels(word) > 1:
                pieces = word.split('+')
                assert len(pieces) == 2
                self._data[word.replace('+', '')] = len(pieces[0])  # accented character index

    def __call__(self, word):
        accent = self._data.get(word.lower())
        if accent is None:
            return None
        word = list(word)
        word.insert(accent + 1, '\u0301')
        word = ''.join(word)
        return word

def sample(onnx_model, vocab, data, words=['станок', 'перевязав', 'КРОВАТИ', 'красота', 'здоровье', 'Задница']):

    print('AI')
    predictor = MLPredictor(onnx_model, vocab)
    for word in words:
        predicted = predictor(word)
        print(word, '==>', predicted)

    print('VOCAB')
    vocab_predictor = VocabPredictor(data)
    for word in words:
        predicted = vocab_predictor(word)
        print(word, '==>', predicted)

    print('BEST')
    best_predictor = Predictor(onnx_model, vocab, data)
    for word in words:
        predicted = best_predictor(word)
        print(word, '==>', predicted)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Predicts russian accents')
    parser.add_argument('-m', '--model', default='model-accentru.onnx', help='File name of the model ONNX file')
    parser.add_argument('-v', '--vocab', default='vocab-accentru.json', help='File name of the vocab JSON file')
    parser.add_argument('-d', '--data',  default='data/stress.dict', help='File name of the stress dictionary file')

    args = parser.parse_args()

    sample(args.model, args.vocab, args.data)