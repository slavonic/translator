import json
import onnxruntime as ort
import re
import numpy as np

class Predictor:
    RE = "[абвгдеёжзийклмнопрстуфхцчшщьыъэюя'\u0301]+"

    def __init__(self, onnx_model, vocab, data_dict):
        self._ml_predictor = MLPredictor(onnx_model, vocab)
        self._vocab_predictor = VocabPredictor(data_dict)

    def __call__(self, word):
        if 'ё' in word.lower() or num_vowels(word) < 2:
            return word
        word = word.replace("'", '\u0301')
        if '\u0301' in word:
            return word
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
RE_WORD = '^[абвгдеёжзийклмнопрстуфхцчшщьыъэюя]+$'

def num_vowels(word):
    return len(re.split(RE_VOWELS, word, flags = re.IGNORECASE)) - 1

class VocabPredictor:
    def __init__(self, data_dict):
        with open(data_dict, encoding='utf-8') as f:
            words = [l.strip() for l in f if l.strip()]
        self._data = {}
        for word in words:
            assert word.lower() == word
            assert num_vowels(word) > 1
            pieces = word.split('\u0301')
            assert len(pieces) == 2
            self._data[word.replace('\u0301', '')] = len(pieces[0]) - 1  # accented character index
        print(f'Loaded: {len(self._data)} dictionary words')

    def __call__(self, word):
        accent = self._data.get(word.lower())
        if accent is None:
            return None
        word = list(word)
        word.insert(accent + 1, '\u0301')
        word = ''.join(word)
        return word

def sample(onnx_model, vocab, data, words=['станок', 'перевязав', 'КРОВАТИ', 'красота', 'здоровье', 'Задница', 'стрёмно', 'дети']):
    predictor = Predictor(onnx_model, vocab, data)
    for word in words:
        predicted = predictor(word)
        print(word, '==>', predicted)

    out_text = stress_text(predictor, '...гляжу -- поднимается медленно в гору лошадка везущая хворосту воз...')
    print(''.join(out_text))

def stress_text(predictor, text):
    offset = 0
    for mtc in re.finditer(Predictor.RE, text, flags=re.IGNORECASE):
        s, e = mtc.span()
        if offset < s:
            yield text[offset:s]
        yield predictor(text[s:e])
        offset = e
    if offset < len(text):
        yield text[offset:]

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Predicts russian accents')
    parser.add_argument('-m', '--model', default='model-accentru.onnx', help='File name of the model ONNX file')
    parser.add_argument('-v', '--vocab', default='vocab-accentru.json', help='File name of the vocab JSON file')
    parser.add_argument('-d', '--data',  default='data/ru_stress_compressed.txt', help='File name of the stress dictionary file')

    args = parser.parse_args()

    sample(args.model, args.vocab, args.data)