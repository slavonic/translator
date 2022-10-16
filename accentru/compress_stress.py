import json
import onnxruntime as ort
import re
import numpy as np
from .predictor import MLPredictor

def compress_stress(onnx_model, vocab, data, data_compressed):

    predictor = MLPredictor(onnx_model, vocab)
    with open(data, encoding='utf-8') as f:
        words = [l.strip() for l in f if l.strip()]

    mistakes = []
    count = 0
    for word in words:
        count += 1
        if count % 1000 == 0:
            print(count, '/', len(words), round(len(mistakes) / count, 3))
        predicted = predictor(word.replace('\u0301', ''))
        if predicted != word:
            mistakes.append(word)
            print(word, '==>', predicted)

    with open(data_compressed, 'w') as f:
        for word in mistakes:
            f.write(word + '\n')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Compresses train stress dictionary by removing words that model predicts correctly')
    parser.add_argument('-m', '--model', default='model-accentru.onnx', help='File name of the model ONNX file')
    parser.add_argument('-v', '--vocab', default='vocab-accentru.json', help='File name of the vocab JSON file')
    parser.add_argument('-d', '--data',  default='data/ru_stress.txt', help='File name of the stress file')
    parser.add_argument('-o', '--out',   default='data/ru_stress_compressed.txt', help='File name of the output compressed stress file')

    args = parser.parse_args()

    compress_stress(args.model, args.vocab, args.data, args.out)